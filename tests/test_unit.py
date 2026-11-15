import pytest
from agenda_bella.services import money,period,text,ValidationError

@pytest.mark.parametrize('value,expected',[('30,00',3000),('0',0),('12.99',1299)])
def test_money(value,expected):
    assert money(value)==expected

@pytest.mark.parametrize('value',['-1','NaN','Infinity','1.001','abc','1000000'])
def test_invalid_money(value):
    with pytest.raises(ValidationError): money(value)

@pytest.mark.parametrize('start,end',[('2026-10-20T15:00','2026-10-20T14:00'),('bad','bad'),('2026-10-20T14:00','2026-10-21T15:00')])
def test_invalid_period(start,end):
    with pytest.raises(ValidationError): period(start,end)

def test_html_rejected():
    with pytest.raises(ValidationError): text('<script>alert(1)</script>','Nome')
