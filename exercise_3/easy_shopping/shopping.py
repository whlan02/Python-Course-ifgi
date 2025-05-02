class ShoppingCart:
    # initialize an empty dictionary of items and their quantities
    def __init__(self):
        self.items = {}

    # function to add an item in a defined quantity to the dict
    def add_item(self, item, quantity):
        if quantity > 0:
            # only adding if the item already exits
            if item in self.items:
                self.items[item] += quantity
                print(f"{quantity} of {item} were added to {item}.")
            # adding a new item
            else:
                self.items[item] = quantity
                print(f"{quantity} of {item} were added to the cart.")
        else:
            print("The quantity must be higher than zero!")
        
    # function to delete a quantity of items from the cart
    def remove_item_quantity(self, item, quantity):
        # check if the item exists
        if item in self.items:
            # no more items than existing can be deleted. If the whole item should be deleted the function "remove_whole_item" should be used
            if quantity < self.items[item] and quantity > 0:
                self.items[item] -= quantity
                print(f"{quantity} of {item} were deleted from the cart.")
            else:
                print(f"This quantity too high to remove, lower than one or of a wrong datatype!")
        else:
            print(f"{item} is not on your cart!")

    # function to remove an item completely
    def remove_whole_item(self, item):
        # check if item exists and delete it
        if item in self.items:
            del self.items[item]
            print(f"All {item} was deleted from the cart.")
        else:
            print(f"{item} is not on your cart!")

    # function to display the cart items ant their quantities
    def show_cart(self):
        # check if the cart contains items
        if self.items:
            print("Your items (item: quantity):")
            # print items after each other
            for item, quantity in self.items.items():
                print(f"{item}: {quantity}")
        else:
            print("No items in your cart!")

    # show total amount of items on the cart
    def total_amount(self):
        print(f"Total amount of items on your cart: {sum(self.items.values())}")


cart = ShoppingCart()
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