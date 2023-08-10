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

***
Bazując na aplikacji do zarządzania firmą, stwórz jej webowy odpowiednik.
Na stronie głównej wyświetl informację na temat stanu konta, magazynu oraz trzy formularze:
zakup, sprzedaż, zmiana salda.
Formularz zakupu powinien zawierać trzy pola: nazwa produktu, cena i ilość
Formularz sprzedaży powinien zawierać dwa pola: nazwa produktu i ilość
Formularz zmiany salda powinien zawierać jedno pole: wartość zmiany salda
Dodatkowo utwórz drugą podstronę zawierającą historię wykonanych operacji.
Podstrona powinna być dostępna pod URL "/historia/" oraz "/historia/<start>/<koniec>"
W przypadku "/historia/" na stronie ma się pojawić cała dostępna historia.
W przypadku "/historia/<start>/<koniec>" zależnie od podanych wartości w <start> i <koniec>,
mają się pojawić wskazane linie, np. od 3 do 12. W przypadku podania złego (lub nieistniejącego zakresu indeksów), 
program poinformuje o tym użytkownika i wyświetli możliwy do wybrania zakres historii.
Zadanie wciąż powinno korzystać z plików do przechowywania stanu konta, magazynu i historii.

"""

import json
from flask import Flask, request, render_template, redirect, url_for


app = Flask(__name__)

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

    def execute(self, command, **kwargs):
        if command == "saldo":
            amount = kwargs.get('amount')
            if self.account + amount < 0:
                action = "Nie można mieć ujemnego salda!"
                self.history.append(action)
            else:
                self.account += amount
                action = f"Zmieniono saldo o {amount}"
                self.history.append(action)
                self.save_account(self.account)

        elif command == "sprzedaż":
            name = kwargs.get('name')
            quantity = kwargs.get('quantity')
            price = kwargs.get('price')

            if name in self.warehouse:
                if self.warehouse[name] >= quantity:
                    self.warehouse[name] -= quantity
                    total_price = price * quantity
                    self.account += total_price
                    action = f"Sprzedano {quantity} sztuk produktu '{name}' za {total_price} zł"
                    self.history.append(action)
                    self.save_warehouse(self.warehouse)
                    self.save_account(self.account)
                else:
                    action = "Nie wystarczająca ilość produktu w magazynie"
                    self.history.append(action)
            else:
                action = "Produkt nie istnieje w magazynie"
                self.history.append(action)

        elif command == "zakup":
            name = kwargs.get('name')
            price = kwargs.get('price')
            quantity = kwargs.get('quantity')

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
                self.save_account(self.account)
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

        self.save_history(self.history)

    def assign(self):
        print("Witaj w programie zarządzania firmą!")
        while True:
            print("\nDostępne komendy:")
            print("saldo\n"
                  "sprzedaż\n"
                  "zakup\n"
                  "konto\n"
                  "lista\n"
                  "magazyn\n"
                  "przegląd\n"
                  "koniec")

            command = input("Wprowadź komendę: ")

            if command == "koniec":
                self.save_history(self.history)
                break

            self.execute(command)

manager = Manager()
@app.route('/', methods=['GET'])
def index():
    manager = Manager()
    account = manager.account
    warehouse = manager.warehouse

    return render_template('index.html', account=account, warehouse=warehouse, prices=manager.prices)

@app.route('/zakup', methods=['POST'])
def zakup():
    global manager
    name = request.form.get('name')
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    manager.execute("zakup", name=name, price=price, quantity=quantity)
    return redirect('/')


@app.route('/sprzedaz', methods=['POST'])
def sprzedaz():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    quantity = int(request.form.get('quantity'))
    manager.execute("sprzedaż", name=name, price=price, quantity=quantity)

    message = f"Sprzedano {quantity} sztuk produktu '{name}' za {price * quantity} zł"
    manager.history.append(message)
    manager.save_history(manager.history)

    return redirect('/')


@app.route('/saldo', methods=['POST'])
def saldo():
    global manager
    if 'amount' not in request.form:
        return "Brak podanej kwoty", 400

    amount = float(request.form['amount'])
    if amount is None or amount <= 0:
        return "Niepoprawna kwota", 400

    manager.execute("saldo", amount=amount)
    return redirect('/')


@app.route('/historia', methods=['GET'])
def historia():
    manager = Manager()
    return render_template('historia.html', historia=manager.history)


if __name__ == "__main__":
    app.run()