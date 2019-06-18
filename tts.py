# Import the required module for text  
# to speech conversion 
from gtts import gTTS 
  
# This module is imported so that we can  
# play the converted audio 
import os 
  
# The text that you want to convert to audio 
mytext = u"""పొలాల నన్నీ ,
హలాల దున్నీ,
ఇలాతలంలో హేమం పిండగ-
జగానికంతా సౌఖ్యం నిండగ-
విరామ మెరుగక పరిశ్రమించే,
బలం ధరిత్రికి బలి కావించే,
కర్షక వీరుల కాయం నిండా
కాలువకట్టే ఘర్మజలానికి,
ఘర్మజలానికి,
ధర్మజలానికి,
ఘర్మజలానికి ఖరీదు లేదోయ్!"""
  
# Language in which you want to convert 
language = 'te'
  
# Passing the text and language to the engine,  
# here we have marked slow=False. Which tells  
# the module that the converted audio should  
# have a high speed 
myobj = gTTS(text=mytext, lang=language, slow=False) 
  
# Saving the converted audio in a mp3 file named 
# welcome  
myobj.save("pratijna.mp3") 
  
# Playing the converted file 
os.system("mpg123 pratijna.mp3") 
