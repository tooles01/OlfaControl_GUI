'''
Final valve widget

This will connect to an Arduino and send something when the button is pushed


ST 5/21/2026
'''


from PyQt5.QtWidgets import *

class Final_Valve(QGroupBox):

    def __init__(self):
        super().__init__()

        self.setTitle('Final Valve')

        self.final_valve_button = QPushButton(text='Final Valve',checkable=True)
        self.final_valve_button.toggled.connect(self.fv_btn_toggled)

        layout = QHBoxLayout()
        layout.addWidget(self.final_valve_button)
        self.setLayout(layout)



    def fv_btn_toggled(self,checked):
        if checked:
            print('final valve was checked')

        else:
            print('final valve was unchecked')
