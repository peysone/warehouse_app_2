"""Napisz program, który będzie rejestrował operacje na koncie firmy i stan magazynu.

Program po uruchomieniu wyświetla informację o dostępnych komendach:

saldo
sprzedaż
zakup
konto
lista
magazyn
przegląd
koniec

Po wprowadzeniu odpowiedniej komendy, aplikacja zachowuje się w unikalny sposób dla każdej z nich:

saldo - Program pobiera kwotę do dodania lub odjęcia z konta.
sprzedaż - Program pobiera nazwę produktu, cenę oraz liczbę sztuk. Produkt musi znajdować się w magazynie. Obliczenia respektuje względem konta i magazynu (np. produkt "rower" o cenie 100 i jednej sztuce spowoduje odjęcie z magazynu produktu "rower" oraz dodanie do konta kwoty 100).
zakup - Program pobiera nazwę produktu, cenę oraz liczbę sztuk. Produkt zostaje dodany do magazynu, jeśli go nie było. Obliczenia są wykonane odwrotnie do komendy "sprzedaz". Saldo konta po zakończeniu operacji „zakup” nie może być ujemne.
konto - Program wyświetla stan konta.
lista - Program wyświetla całkowity stan magazynu wraz z cenami produktów i ich ilością.
magazyn - Program wyświetla stan magazynu dla konkretnego produktu. Należy podać jego nazwę.
przegląd - Program pobiera dwie zmienne „od” i „do”, na ich podstawie wyświetla wszystkie wprowadzone akcje zapisane pod indeksami od „od” do „do”. Jeżeli użytkownik podał pustą wartość „od” lub „do”, program powinien wypisać przegląd od początku lub/i do końca. Jeżeli użytkownik podał zmienne spoza zakresu, program powinien o tym poinformować i wyświetlić liczbę zapisanych komend (żeby pozwolić użytkownikowi wybrać odpowiedni zakres).
koniec - Aplikacja kończy działanie."""

"""
Saldo konta oraz magazyn mają zostać zapisane do pliku tekstowego, 
a przy kolejnym uruchomieniu programu ma zostać odczytany. 
Zapisać należy również historię operacji (przegląd), 
która powinna być rozszerzana przy każdym kolejnym uruchomieniu programu."""



"""
*
Rozbuduj program do zarządzania firmą. Wszystkie funkcjonalności 
(komendy, zapisywanie i czytanie przy użyciu pliku itp.) pozostają bez zmian.

Stwórz clasę Manager, która będzie implementowała dwie kluczowe metody - execute i assign. 
Przy ich użyciu wywołuj poszczególne fragmenty aplikacji. Metody execute i assign powinny zostać zaimplementowane
zgodnie z przykładami z materiałów do zajęć.

Niedozwolone są żadne zmienne globalne, wszystkie dane powinny być przechowywane wewnątrz obiektu Manager.
"""

import json

class Manager:
    def __init__(self):
        self.account = self.load_account()
        self.warehouse = self.load_warehouse()
        self.prices = {}
        self.history = self.load_history()

    def save_account(self, account):
        with open('saldo.txt', 'w') as file:
            json.dump(account, file)

    def save_warehouse(self, warehouse):
        with open('magazyn.txt', 'w') as file:
            json.dump(warehouse, file)

    def save_history(self, history):
        with open('historia.txt', 'w') as file:
            for operation in history:
                file.write(operation + '\n')

    def load_account(self):
        try:
            with open('saldo.txt', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def load_warehouse(self):
        try:
            with open('magazyn.txt', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_history(self):
        try:
            with open('historia.txt', 'r') as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            return []

    def modify_data(self, data, changes):
        for change in changes:
            change_values = change.split(',')
            column = int(change_values[0])
            row = int(change_values[1])
            value = change_values[2]
            if row < len(data) and column < len(data[row]):
                data[row][column] = value
            else:
                self.history.append(f"Warning: Ignoring change at ({column}, {row}). Coordinates out of range.")

    def execute(self, command):
        if command == "saldo":
            amount = float(input("Wprowadź kwotę: "))
            if self.account + amount < 0:
                action = "Nie można mieć ujemnego salda!"
                self.history.append(action)
            else:
                self.account += amount
                action = f"Dodano {amount} do konta"
                self.history.append(action)
                self.save_account(self.account)

        elif command == "sprzedaż":
            name = input("Wprowadź nazwę produktu: ")
            if name in self.warehouse:
                price = self.prices[name]
                quantity = int(input("Wprowadź liczbę sztuk: "))
                if self.warehouse[name] >= quantity:
                    self.warehouse[name] -= quantity
                    total_price = price * quantity
                    self.account += total_price
                    action = f"Sprzedano {quantity} sztuk produktu '{name}' za {total_price} zł"
                    self.history.append(action)
                else:
                    action = "Nie wystarczająca ilość produktu w magazynie"
                    self.history.append(action)
            else:
                action = "Produkt nie istnieje w magazynie"
                self.history.append(action)

        elif command == "zakup":
            name = input("Wprowadź nazwę produktu: ")
            price = float(input("Wprowadź cenę: "))
            quantity = int(input("Wprowadź liczbę sztuk: "))

            if self.account >= price * quantity:
                self.account -= price * quantity
                if name in self.warehouse:
                    self.warehouse[name] += quantity
                else:
                    self.warehouse[name] = quantity
                self.prices[name] = price
                action = f"Zakupiono {quantity} sztuk produktu '{name}' za {price * quantity} zł"
                self.history.append(action)
                self.save_warehouse(self.warehouse)
            else:
                action = "Brak wystarczających środków na koncie"
                self.history.append(action)

        elif command == "konto":
            action = f"Stan konta: {self.account}"
            self.history.append(action)

        elif command == "lista":
            action = "Stan magazynu:"
            self.history.append(action)
            for name, quantity in self.warehouse.items():
                if name in self.prices:
                    price = self.prices[name]
                    action = f"{name}: ilość - {quantity}, cena - {price} zł"
                    self.history.append(action)

        elif command == "magazyn":
            action = "Stan magazynu:"
            self.history.append(action)
            for name, quantity in self.warehouse.items():
                action = f"{name}: ilość - {quantity}"
                self.history.append(action)

        elif command == "przegląd":
            start_index = int(input("Podaj indeks 'od': "))
            end_index = int(input("Podaj indeks 'do': "))

            if not self.history:
                action = "Brak zapisanych operacji."
                self.history.append(action)
            elif start_index < 0 or end_index >= len(self.history):
                action = f"Nieprawidłowy zakres. Dostępne indeksy: od 0 do {len(self.history) - 1}"
                self.history.append(action)
            elif start_index > end_index:
                action = "'Od' nie może być większe niż 'do'."
                self.history.append(action)
            else:
                idx = self.history[start_index:end_index + 1]
                for index, operation in enumerate(idx):
                    action = f"[{start_index + index}] {operation}"
                    self.history.append(action)

        elif command == "koniec":
            pass

    def assign(self):
        print("Witaj w programie zarządzania firmą!")
        while True:
            print("\nDostępne komendy:")
            print("saldo\nsprzedaż\nzakup\nkonto\nlista\nmagazyn\nprzegląd\nkoniec")

            command = input("Wprowadź komendę: ")

            if command == "koniec":
                self.save_history(self.history)
                break

            self.execute(command)

if __name__ == "__main__":
    manager = Manager()
    manager.assign()
