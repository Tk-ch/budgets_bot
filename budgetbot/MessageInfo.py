class MessageInfo: 
  def __init__(self, text, markup, delete = False, reset_markup = False): 
    self.text = text
    self.markup = markup
    self.delete = delete
    self.reset_markup = reset_markup
    
    