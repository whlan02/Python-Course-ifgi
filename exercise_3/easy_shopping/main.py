import calculator
import shopping

def main():
    # Create calculator instance
    calc = calculator.Calculator()
    
    # Test case 1: 7+5
    print("7 + 5 =", calc.add(7, 5))
    
    # Test case 2: 34-21
    print("34 - 21 =", calc.subtract(34, 21))
    
    # Test case 3: 54*2
    print("54 * 2 =", calc.multiply(54, 2))
    
    # Test case 4: 144/2
    print("144 / 2 =", calc.divide(144, 2))
    
    # Test case 5: 45/0
    try:
        result = calc.divide(45, 0)
        print("5. 45 / 0 =", result)
    except ZeroDivisionError as e:
        print("5. 45 / 0 = Error:", str(e))

    # test the shopping cart
    print("")
    cart = shopping.ShoppingCart()
    cart.show_cart()
    cart.total_amount()
    cart.add_item("Banana", 3)
    cart.add_item("Apple", 2)
    cart.add_item("Tomato", 50)
    cart.add_item("Tomato", 50)
    cart.show_cart()
    cart.total_amount()
    cart.remove_item_quantity("Tomato", 10)
    cart.remove_item_quantity("Tomato", 100)
    cart.remove_item_quantity("Hello", 100)
    cart.show_cart()
    cart.total_amount()
    cart.remove_whole_item("Banana")
    cart.remove_whole_item("Hello")
    cart.show_cart()
    cart.total_amount()


if __name__ == "__main__":
    main()
