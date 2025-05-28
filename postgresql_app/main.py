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


# CO MUSZĘ JESZCZE ZROBIĆ:
# zmodyfikowac Menu - usunac int (self.choice) ✅
# usunac niepotrzebne elementy - in progress    ✅
#  WYWALIC kolumne presc_tab z bazy danych  ✅
# nie wiem czy sie automatycznie connection zamyka 🚩 - może użyc with? // na końcu main connection.close ✅// PatientMenu - w opcji exit wywołuje connection_close ✅
# dodac assign - zeby w pelni móc przypisywac pacjentów i recepty
# moze przeniesc slowniki do toml?
# zbudowac jakis basic interface - moze we flasku? 
# poprawic id w tabelach jako PK - postanowilam, że zostawie jak jest i dopisze wyjasnienie w documentacji 💡
# zmienic nazwy FK np presc_id na pełne prescription_id - postanowilam, że tylko dopisze'Fk' na końcu foreign keys 💡
# podzial na pliki
# dodac rollback przy errorach zw z baza danych
# dodac timestamp zamiast daty do recept 💡