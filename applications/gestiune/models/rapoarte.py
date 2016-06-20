# coding: utf8

def raport_facturi_luna():
    raport = db.executesql('''
        SELECT `raport_vanzari`.`tip_factura`
            ,SUM(`raport_vanzari`.`suma_factura`) AS `Total`
            ,SUM(`raport_vanzari`.`puncte_folosite_factura`) AS `PuncteFolosite`
            ,SUM(`raport_vanzari`.`puncte_acordate_factura`) AS `PuncteAcordate`
            ,SUM(`raport_vanzari`.`discount_acordat`) AS `Discount`
        FROM `raport_vanzari`
        WHERE MONTH(`raport_vanzari`.`data_adaugare_factura`) = MONTH(NOW())
            AND YEAR(`raport_vanzari`.`data_adaugare_factura`) = YEAR(NOW())    
        GROUP BY 
            `raport_vanzari`.`tip_factura`;''', as_dict = True)
    return raport

def raport_facturi_zi(data):
    raport = db.executesql('''
        SELECT `raport_vanzari`.`tip_factura`
            ,SUM(`raport_vanzari`.`suma_factura`) AS `Total`
            ,SUM(`raport_vanzari`.`puncte_folosite_factura`) AS `PuncteFolosite`
            ,SUM(`raport_vanzari`.`puncte_acordate_factura`) AS `PuncteAcordate`
            ,SUM(`raport_vanzari`.`discount_acordat`) AS `Discount`
        FROM `raport_vanzari`
        WHERE `raport_vanzari`.`data_adaugare_factura` LIKE \'{0}%\'
        GROUP BY 
            `raport_vanzari`.`tip_factura`;'''.format(data), as_dict = True)
    return raport
    
def raport_useri_luna():
    raport = db.executesql('''
        SELECT `raport_vanzari`.`username`
            ,SUM(`raport_vanzari`.`suma_factura`) AS `Total`
            ,SUM(`raport_vanzari`.`puncte_folosite_factura`) AS `PuncteFolosite`
            ,SUM(`raport_vanzari`.`puncte_acordate_factura`) AS `PuncteAcordate`
            ,SUM(`raport_vanzari`.`discount_acordat`) AS `Discount`
        FROM `raport_vanzari`
        WHERE MONTH(`raport_vanzari`.`data_adaugare_factura`) = MONTH(NOW())
            AND YEAR(`raport_vanzari`.`data_adaugare_factura`) = YEAR(NOW())    
        GROUP BY 
            `raport_vanzari`.`username`;''', as_dict = True)
    return raport
    
def raport_useri_zi(data):
    raport = db.executesql('''
        SELECT `raport_vanzari`.`username`
            ,SUM(`raport_vanzari`.`suma_factura`) AS `Total`
            ,SUM(`raport_vanzari`.`puncte_folosite_factura`) AS `PuncteFolosite`
            ,SUM(`raport_vanzari`.`puncte_acordate_factura`) AS `PuncteAcordate`
            ,SUM(`raport_vanzari`.`username`) AS `Discount`
        FROM `raport_vanzari`
        WHERE `raport_vanzari`.`data_adaugare_factura` LIKE \'{0}%\'
        GROUP BY 
            `raport_vanzari`.`username`;'''.format(data), as_dict = True)
    return raport
