from flask import render_template

class TBView:
    @staticmethod
    def render_medform_list(medforms):
        return render_template('tb_list.html', medforms=medforms)