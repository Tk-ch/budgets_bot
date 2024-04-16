class MessageInfo: 
  def __init__(self, text, markup = None, delete = False, delete_users_message = False, reset_markup = False): 
    self.text = text
    self.markup = markup
    self.delete = delete
    self.delete_users_message = delete_users_message
    self.reset_markup = reset_markup
    
    