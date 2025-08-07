def has_item(dict):
     for k in dict.keys():
          if k == "Bad thing":
               print("Found")
          else:
               print("Not found")
has_item( {'Rating': '3', 'Benefits': 'Эмульгатор и стабилизатор.', 'Bad thing': 'Может вызывать раздражение кожи у некоторых людей.'})