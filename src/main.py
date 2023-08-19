from kratos.scrapper.carrefour import Carrefour
import json

if __name__ == '__main__':
    carrefour = Carrefour()
    products = carrefour.extract_all_products()
    print(json.dumps(products, indent=4))

