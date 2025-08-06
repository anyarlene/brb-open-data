import os
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import certifi
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yaml

import zlib

logger = logging.getLogger(__name__)

def get_project_root() -> Path:
    """
    Return the project root directory (where pyproject.toml lives).
    Assumes this file is at analytics/src/etl/download_manager.py
    """
    # __file__ → .../analytics/src/etl/download_manager.py
    return Path(__file__).resolve().parents[2]  # parents[0]=etl, [1]=src, [2]=analytics root

def get_combined_ca_path() -> Path:
    """
    Return the Path to the combined CA bundle: certifi + project-specific intermediate.
    If no intermediate found, return None.
    """
    project_root = get_project_root()
    # Path to the intermediate in your repo
    intermediate = project_root / "Config" / "ca" / "RapidSSL_TLS_RSA_CA_G1.pem"
    if intermediate.is_file():
        # Combine certifi bundle + intermediate into a temp file or a persistent file under project
        combined = project_root / "Config" / "ca" / "combined_cacert.pem"
        # If not exists or older than certifi or intermediate, regenerate
        certifi_path = Path(certifi.where())
        # Check timestamps
        try:
            regen = False
            if not combined.exists():
                regen = True
            else:
                ts_combined = combined.stat().st_mtime
                # regenerate if certifi or intermediate is newer
                if certifi_path.stat().st_mtime > ts_combined or intermediate.stat().st_mtime > ts_combined:
                    regen = True
            if regen:
                # Read certifi bundle and intermediate, write combined
                with open(certifi_path, "rb") as f:
                    base = f.read()
                with open(intermediate, "rb") as f:
                    inter = f.read()
                with open(combined, "wb") as f:
                    f.write(base)
                    f.write(b"\n")
                    f.write(inter)
                logger.info(f"Generated combined CA bundle at {combined}")
        except Exception as e:
            logger.warning(f"Could not generate combined CA bundle: {e}")
            return None
        return combined
    else:
        # No project-specific intermediate found
        return None

def get_requests_session() -> requests.Session:
    """
    Return a requests.Session with retries and SSL verification.
    Uses a combined CA bundle (certifi + project intermediate) if available,
    else falls back to certifi.where().
    """
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    combined_ca = get_combined_ca_path()
    if combined_ca and combined_ca.is_file():
        session.verify = str(combined_ca)
        logger.info(f"Using combined CA bundle at: {combined_ca}")
    else:
        ca = certifi.where()
        session.verify = ca
        logger.info(f"Using certifi CA bundle: {ca}")

    return session

# ... rest of code unchanged ...
def load_sources_config(config_path: Path):
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg_all = yaml.safe_load(f)
    if not isinstance(cfg_all, dict) or "sources" not in cfg_all:
        raise ValueError(f"Invalid config (missing 'sources'): {config_path}")
    return cfg_all["sources"]

def discover_excel_link(page_url: str, pattern: str, session: requests.Session) -> str:
    logger.info(f"Discovering link on page: {page_url}")
    resp = session.get(page_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    regex = re.compile(pattern, re.IGNORECASE)

    # Debug: list all <a> hrefs and their names
    all_hrefs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = Path(href).name
        all_hrefs.append(name)
    logger.info(f"All link filenames on page: {all_hrefs}")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = Path(href).name
        if regex.search(name):
            logger.info(f"Found matching link: {href}")
            return href
    raise ValueError(f"No link matching pattern {pattern!r} on page {page_url}")


def download_and_version_file(
    file_url: str,
    save_dir: Path,
    session: requests.Session,
    sanitize_regex: str = r"[^\w\.-]"
) -> Path:
    logger.info(f"Downloading file from URL: {file_url}")
    resp = session.get(file_url)
    resp.raise_for_status()

    orig_name = Path(file_url).name
    stem = Path(orig_name).stem
    # sanitize name
    sanitized = re.sub(r"\s+", "_", stem)
    sanitized = re.sub(sanitize_regex, "_", sanitized)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")

    # Compute a 5-digit prefix from CRC32 of file_url (or orig_name):
    crc = zlib.crc32(file_url.encode("utf-8")) & 0xFFFFFFFF
    short_id = crc % 100000  # gives 0..99999
    prefix = f"{short_id:05d}"

    date_str = datetime.now().strftime("%Y%m%d")
    ext = Path(orig_name).suffix or ""
    new_filename = f"{prefix}_{sanitized}_{date_str}{ext}"

    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / new_filename
    # Open with 'wb' always overwrites if exists
    with open(save_path, "wb") as f:
        f.write(resp.content)
    logger.info(f"Saved file to: {save_path}")
    return save_path

def process_source(
    name: str,
    entry: dict,
    project_root: Path,
    session: requests.Session
) -> Path:
    url = entry.get("url")
    if not url:
        raise ValueError(f"Source '{name}' missing 'url'")
    local_subdir = entry.get("local_subdir")
    if not local_subdir:
        raise ValueError(f"Source '{name}' missing 'local_subdir'")
    save_dir = project_root / local_subdir

    if re.search(r"\.xls[x]?$", url, re.IGNORECASE):
        file_url = url
    else:
        pattern = entry.get("pattern")
        if not pattern:
            raise ValueError(f"Source '{name}' needs 'pattern' for page {url}")
        href = discover_excel_link(url, pattern, session)
        file_url = urljoin(url, href)

    logger.info(f"[{name}] Final URL: {file_url}")
    return download_and_version_file(file_url, save_dir, session)

def run_all_downloads(config_path: Path = None) -> dict:
    if config_path is None:
        project_root = get_project_root()
        config_path = project_root / "config" / "sources.yml"
    else:
        project_root = config_path.parents[1]

    logger.info(f"Loading config: {config_path}")
    sources = load_sources_config(config_path)
    session = get_requests_session()
    results = {}
    for name, entry in sources.items():
        try:
            saved = process_source(name, entry, project_root, session)
            filename = Path(saved).name
            results[name] = {
                "status": "successful",
                "path": f"File {filename} successfully saved"
            }
            logger.info(f"[{name}] Download succeeded: {saved}")
        except Exception as e:
            logger.error(f"[{name}] Error: {e}")
            results[name] = {
                "status": "failed",
                "path": f"Download failed: {str(e)}"
            }
    return results

def main():
    import argparse, json
    parser = argparse.ArgumentParser(description="Download configured Excel sources")
    parser.add_argument("--config", "-c", help="Path to config YAML (default config/sources.yml)", default=None)
    parser.add_argument("--output-json", "-o", help="Print JSON results", action="store_true")
    parser.add_argument("--verbose", "-v", help="Show detailed progress messages", action="store_true")
    args = parser.parse_args()

    # Only show WARNING and above unless --verbose flag is used
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

    config_path = Path(args.config) if args.config else None
    results = run_all_downloads(config_path)
    if args.output_json:
        print(json.dumps(results, indent=2))
    else:
        for name, res in results.items():
            if res["status"] == "successful":
                print(f"✓ {name}: {res['path']}")
            else:
                print(f"✗ {name}: {res['path']}")

if __name__ == "__main__":
    main()
