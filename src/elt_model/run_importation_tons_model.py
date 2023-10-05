from importation_tons_data_model import ImportationTonsDataModel

if __name__ == "__main__":
    model = ImportationTonsDataModel()
    data = model.fetchAndProcess()
    model.saveProcessedData()
    print(model.displayData())
