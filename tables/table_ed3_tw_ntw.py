from __future__ import print_function
import os, sys
import numpy as np
import pandas as pd
from glob import glob
from collections import OrderedDict

reg_dir = '/home/atom/ongoing/work_worldwide/vol/reg'
fn_o1 = '/home/atom/ongoing/work_worldwide/vol/tile/subreg_multann_O1_err.csv'
out_csv = '/home/atom/ongoing/work_worldwide/tables/revised/ED_Table_3.csv'

df_in = pd.read_csv(fn_o1)

df_1 = df_in[df_in.category=='tw']

df_out = pd.DataFrame()

def sum_regions(df_p):

    # GLOBAL TOTAL
    area_global = np.nansum(df_p.area.values)
    area_nodata_global = np.nansum(df_p.area_nodata.values)
    tarea_global = np.nansum(df_p.tarea.values)

    dmdt_global = np.nansum(df_p.dmdt.values)
    err_dmdt_global = np.sqrt(np.nansum(df_p.err_dmdt.values ** 2))

    dvoldt_global = np.nansum(df_p.dvoldt.values)
    err_dvoldt_global = np.sqrt(np.nansum(df_p.err_dvoldt.values ** 2))

    err_tarea_global = np.sqrt(np.nansum((1 / 100. * df_p.tarea.values) ** 2))
    dhdt_global = np.nansum(df_p.dvoldt.values) / tarea_global
    err_dhdt_global = np.sqrt(
        (err_dvoldt_global / tarea_global) ** 2 + (err_tarea_global * dvoldt_global / (tarea_global ** 2)) ** 2)

    perc_area_res_global = np.nansum(df_p.perc_area_res.values * df_p.area.values) / np.nansum(
        df_p.perc_area_res.values)
    perc_area_meas_global = np.nansum(df_p.perc_area_meas.values * df_p.area.values) / np.nansum(
        df_p.perc_area_meas.values)

    valid_obs_global = np.nansum(df_p.valid_obs.values * df_p.area.values) / np.nansum(df_p.perc_area_res.values)
    valid_obs_py_global = np.nansum(df_p.valid_obs_py.values * df_p.area.values) / np.nansum(df_p.perc_area_res.values)

    df_sum = pd.DataFrame()
    df_sum = df_sum.assign(area=[area_global],area_nodata=[area_nodata_global],dhdt=[dhdt_global],err_dhdt=[err_dhdt_global],dvoldt=[dvoldt_global],err_dvoldt=[err_dvoldt_global]
                                 ,dmdt=[dmdt_global],err_dmdt=[err_dmdt_global],tarea=[tarea_global],perc_area_res=[perc_area_res_global],perc_area_meas=[perc_area_meas_global],valid_obs=[valid_obs_global]
                                 ,valid_obs_py=[valid_obs_py_global])

    return df_sum

# region_names = ['01 Alaska (ALA)','02 Western Canada & USA (WNA)','03 Arctic Canada North (ACN)'
#     ,'04 Arctic Canada South (ACS)','05 Greenland (GRL)', '06 Iceland (ISL)','07 Svalbard and Jan Mayen (SJM)'
#     , '08 Scandinavia (SCA)','09 Russian Arctic (RUA)', '10 North Asia (ASN)','11 Central Europe (CEU)'
#     , '12 Caucasus and Middle East (CAU)', '13 Central Asia (ASC)','14 South Asia West (ASW)', '15 South Asia East (ASE)',
#     '16 Low Latitudes (TRP)','17 Southern Andes (SAN)','18 New Zealand (NZL)','19 Antarctic and Subantarctic (ANT)', 'Total, excl. Greenland and Antarctic','Global total']
region_names = list(OrderedDict.fromkeys(df_1.subreg.tolist()))

df_2 = df_in[np.logical_and(df_in.subreg.isin(region_names),df_in.category=='ntw')]
region_names += ['Global excluding GRL and ANT','Global']

periods = ['2000-01-01_2005-01-01','2005-01-01_2010-01-01','2010-01-01_2015-01-01','2015-01-01_2020-01-01','2000-01-01_2020-01-01']
# periods = ['2000-01-01_2020-01-01']
columns_names = ['2000-2005','2005-2010','2010-2015','2015-2020','2000-2020']
# column_names=['2000-2020']

list_df = [df_1,df_2]
list_df_out = []
for k in range(len(list_df)):

    df= list_df[k]
    list_dh = []
    list_dh_err = []
    list_dm = []
    list_dm_err =[]
    df_out = pd.DataFrame()
    for period in periods:
        df_p = df[df.period==period]

        df_global = sum_regions(df_p)
        df_global['reg']='global'

        df_noperiph = sum_regions(df_p[~df_p.reg.isin([5,19])])
        df_noperiph['reg']='global_noperiph'

        df_full_p = pd.concat([df_p,df_noperiph,df_global])

        column_dh = []
        column_err_dh = []
        for i in range(len(df_full_p)):
            dh = '{:.2f}'.format(df_full_p.dhdt.values[i])
            err_dh= '{:.2f}'.format(2*df_full_p.err_dhdt.values[i])
            column_dh.append(dh)
            column_err_dh.append(err_dh)


        column_dm = []
        column_err_dm = []
        for i in range(len(df_full_p)):
            dm = '{:.1f}'.format(df_full_p.dmdt.values[i])
            err_dm = '{:.1f}'.format(2 * df_full_p.err_dmdt.values[i])
            column_dm.append(dm)
            column_err_dm.append(err_dm)

        list_dh.append(column_dh)
        list_dh_err.append(column_err_dh)
        list_dm.append(column_dm)
        list_dm_err.append(column_err_dm)


    column_str_dh = []
    column_str_dh_err = []
    column_str_dm = []
    column_str_dm_err = []
    column_str_rel_inc = []
    for j in range(len(list_dh[0])):
        list_str_dh = []
        list_str_err_dh = []
        list_str_dm = []
        list_str_err_dm = []
        for i in range(5):
            list_str_dh.append(list_dh[i][j])
            list_str_err_dh.append(list_dh_err[i][j])
            list_str_dm.append(list_dm[i][j])
            list_str_err_dm.append(list_dm_err[i][j])
        final_str_dh = '/'.join(list_str_dh)
        final_str_dh_err = '/'.join(list_str_err_dh)
        final_str_dm = '/'.join(list_str_dm)
        final_str_dm_err = '/'.join(list_str_err_dm)
        column_str_dh.append(final_str_dh + ' ± '+final_str_dh_err)
        # column_str_dh_err.append(final_str_dh_err)
        column_str_dm.append(final_str_dm+ ' ± '+final_str_dm_err)
        # column_str_dm_err.append(final_str_dm_err)
        rel_inc = (float(list_dh[3][j])-float(list_dh[0][j]))/float(list_dh[0][j])
        column_str_rel_inc.append('{:.2f}'.format(rel_inc))

    df_out['dh_sub'] = column_str_dh
    # df_out['dh_err_sub'] = column_str_dh_err
    df_out['dm_sub'] = column_str_dm
    # df_out['dm_err_sub'] = column_str_dm_err
    df_out['rel_inc'] = column_str_rel_inc

    areas = ['{:.0f}'.format(df_full_p.area.values[i] / 1000000) for i in range(len(df_full_p))]
    df_out.insert(loc=0, column='region', value=region_names)
    df_out.insert(loc=1, column='area', value=areas)

    if k == 0:
        cat = 'tw'
    else:
        cat = 'ntw'

    df_out['cat']=cat
    df_out.index = [2*i + k for i in range(len(df_out))]

    list_df_out.append(df_out)

df_final = pd.DataFrame()
df_final['region'] = list_df_out[0]['region']
df_final['area_tw'] = list_df_out[0]['area']
df_final['dhdt_tw'] = list_df_out[0]['dh_sub']
# df_final['err_dhdt_tw'] = list_df_out[0]['dh_err_sub']
df_final['rel_inc_tw'] = list_df_out[0]['rel_inc']
df_final['area_ntw'] = list_df_out[1]['area'].values
df_final['dhdt_ntw'] = list_df_out[1]['dh_sub'].values
# df_final['err_dhdt_ntw'] = list_df_out[1]['dh_err_sub'].values
df_final['rel_inc_ntw'] = list_df_out[1]['rel_inc'].values

df_final.to_csv(out_csv)

