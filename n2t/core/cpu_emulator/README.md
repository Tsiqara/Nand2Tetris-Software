# Final: Hack Simulator

თქვენი დავალებაა ააწყოთ CLI tool-ი რომელიც გააკეთებს Hack ჰარდვეარ პლათფომაზე პროგრამების შესრულების სიმულაციას.


### მოთხოვნები

CLI უნდა:
  1. იღებდეს `.hack` ან `.asm` ფაილს.
  2. შეასრულოს მიწოდებულ ფაილში არსებული პროგრამა.
  3. დააგენერიროს `.json` ფაილი რომელშიც იქნება RAM-ის საბოლოო მდგომარეობა.
    - ფაილის სახელი უნდა დაემთხვას მიწოდებული პროგრამის სახელს.
  4. მიიღოს პროცესორის ციკლების რაოდენობა არგუმენტად.

### ინტერფეისი

დავალების შესასრულებლად გამოიყენეთ python 3.11. პროგრამის გაშვების მაგალითები:

```sh
python -m n2t execute path/to/the/program.hack --cycles 10000
```

```sh
python -m n2t execute path/to/the/program.asm --cycles 10000
```

### გამომავალი მონაცემები

პროგრამის შესრულების შემდეგ უნდა დააგენერიროთ `.json` ფაილი რომელშიც იქნება RAM-ის საბოლოო მდგომარეობა JSON ფორმატში.

```json
{
  "RAM": {
    "0": 259,
    "1": 1000,
    "2": 2000,
    "3": 0,
    "4": 0,
    "256": 123,
    "257": 0,
    "258": 12
  }
}
```

გაითვალისწინეთ, რომ ფაილში გვხვდება მხოლოდ იმ რეგისტრების მნიშვნელობები, რომლებთანაც პროგრამას ჰქონდა ინტერაქცია.

### შენიშვნები

- შემომავალი ფაილის მისამართი შეიძლება იყოს სრული (absolute) ან ფარდობითი (relative).
- CLI უნდა იყოს აგნოსტიკური ოპერაციული სისტემის მიმართ. (უნდა ეშვებოდეს Windows, Unix...)
- გამომავალ ფაილს უნდა ჰქონდეს იგივე სახელი რაც შემავალ ფაილს (მხოლოდ განსხვავებული გაფართოება).
- შეგიძლიათ ჩათვალოთ რომ შემავალი ფაილი შეიცავს ვალიდურ პროგრამას.
- ეკრანის და კლავიატურის სიმულაცია არ მოგეთხოვებათ.


Keep python conventions in mind:
  - variable_name
  - function_name
  - ClassName
  - CONSTANT_NAME
  - file_name.py
