# Running the Local Server

This guide explains how to run and access the BRB Open Data website locally or make it accessible to other machines on your network.

## Starting the Server

1. Navigate to the website directory:
```bash
cd website
```

2. Run the server using Poetry:
```bash
poetry run python serve.py
```

By default, the server will run on port 8000 and be accessible from other machines. You can customize the port and binding address using arguments:

```bash
poetry run python serve.py --port 8080 --bind 0.0.0.0
```

## Accessing the Website

Once the server is running, you can access the website in two ways:

- **From the same machine**: 
  - Open your browser and go to: http://localhost:8000

- **From other machines on the network**: 
  - Open your browser and go to: http://<your-ip-address>:8000
  - Replace `<your-ip-address>` with your computer's actual IP address on the network
  - You can find your IP address by running `ipconfig` (Windows) or `ifconfig` (Linux/Mac) in the terminal

## Troubleshooting

If you encounter any issues:

1. Make sure you're in the website directory when running the server
2. Check that port 8000 is not already in use
3. If accessing from another machine doesn't work:
   - Verify both machines are on the same network
   - Check if your firewall is blocking incoming connections
   - Try using a different port with the `--port` argument