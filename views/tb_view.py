from flask import render_template

class TBView:
    @staticmethod
    def render_medform_list(medforms):
        return render_template('tb_list.html', medforms=medforms)
    
    @staticmethod
    def render_medical_form_result(tb_result, tb_probability):
        return render_template('results.html', result=tb_result, probability=tb_probability)