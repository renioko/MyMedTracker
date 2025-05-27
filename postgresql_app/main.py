from menu.main_menu import Menu

def main():
    menu = Menu(0, 0)
    menu.display_menu()
    menu_object = menu.choose_menu_object()
    menu.object_choice = menu_object

    menu.display_options(menu_object)
    choice_option = menu.choose_option(menu_object)
    menu.activate_menu_child_class(menu_object, choice_option)

if __name__ == '__main__':
    main()