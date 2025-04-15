
# donuts
# Given an integer count of a number of donuts, return a string
# of the form 'Number of donuts: <count>', where <count> is the number
# passed in. However, if the count is 10 or more, then use the word'many'
# instead of the actual count.
# So donuts(5) returns 'Number of donuts: 5'
# and donuts(23) returns 'Number of donuts: many'
def donuts(count):
    if isinstance(count, int) == False:
        string = "Input must be an Integer"
    elif count < 10:
        string = f"Number of donuts: {count}"
    else: 
        string = "Number of donuts: many"
    return string

# verbing
# Given a string, if its length is at least 3,
# add 'ing' to its end.
# Unless it already ends in 'ing', in which case
# add 'ly' instead.
# If the string length is less than 3, leave it unchanged.
# Return the resulting string.
def verbing(s):
    
    return 

# Remove adjacent
# Given a list of numbers, return a list where
# all adjacent == elements have been reduced to a single element,
# so [1, 2, 2, 3] returns [1, 2, 3]. You may create a new list or
# modify the passed in list.
def remove_adjacent(nums):
    if not nums:  #if the list is empty, return an empty list
        return []
    
    result = [nums[0]]  #initialize the result list, add the first element
    
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1]:  #only add the current element when it is different from the previous one
            result.append(nums[i])
    
    return result

def main():
    print('donuts')
    print(donuts(4))
    print(donuts(9))
    print(donuts(10))
    print(donuts('twentyone'))
    print(donuts(1.2))
    print('verbing')
    print(verbing('hail'))
    print(verbing('swiming'))
    print(verbing('do'))
    print('remove_adjacent')
    print(remove_adjacent([1, 2, 2, 3]))
    print(remove_adjacent([2, 2, 3, 3, 3]))
    print(remove_adjacent([]))
    # Standard boilerplate to call the main() function.

if __name__ == '__main__':
    main()
