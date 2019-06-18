#!/usr/bin/python
# -*- coding: utf8 -*-
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.add_font('lakkireddy', '', 'LakkiReddy.ttf', uni=True)
pdf.set_font('lakkireddy','', 16)
pdf.cell(40,10,u'హలో ప్రపంచమా!')
pdf.output('test.pdf','F')

