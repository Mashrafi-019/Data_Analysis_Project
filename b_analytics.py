import pandas as pd
from datetime import datetime,timedelta

def get_current_stock(sales_df,purchase_df,product_id,):
    quantity_purchased = purchase_df[purchase_df['product_id']==product_id]['quantity_purchased'].sum()
    quantity_sold = sales_df[sales_df['product_id']== product_id]['quantity_sold'].sum()
    quantity_stocked = quantity_purchased - quantity_sold
    return quantity_stocked

def get_profit(products_df,sales_df,product_id):
    product = products_df[products_df['product_id']==product_id]
    quantity_sold=sales_df[sales_df['product_id']==product_id]['quantity_sold'].sum()
    profit_per_sale = product['selling_price'] - product['cost_price']
    profit_per_sale= profit_per_sale.iloc[0]
    total_profit = profit_per_sale * quantity_sold
    return  total_profit

def is_slow_moving(sales_df,product_id):
    start_date = datetime.strptime('2024-12-31','%Y-%m-%d').date()
    cutoff_date = start_date - timedelta(days = 90)
    last_90_days_sale = sales_df[(sales_df['product_id']==product_id) & (sales_df['sale_date']>=cutoff_date)]
    total_recent_sale = last_90_days_sale['quantity_sold'].sum()
    return total_recent_sale <40

def get_stock_status(products_df,product_id):
    product = products_df[products_df['product_id'] == product_id].iloc[0]
    stock = product['current_Stock']
    reorder = product['reorder_level']
    if stock < reorder:return 'Understocked'
    elif stock > reorder * 10 : return 'Overstocked'
    else : return 'Properly Stocked'

def get_revenue(products_df,sales_df,product_id):
    selling_price = products_df[products_df['product_id']==product_id]['selling_price'].iloc[0]
    quantity_sold = sales_df[sales_df['product_id']==product_id]['quantity_sold'].sum()
    revenue = selling_price * quantity_sold
    return revenue

def get_sales_between_dates(sales_df,start_date,end_date,locations):
    return(sales_df[
    (sales_df['sale_date']>=start_date)&
    (sales_df['sale_date']<=end_date)&
    (sales_df['location'].isin(locations))
])

def get_categories(products_df,cataegory):
    return products_df[products_df['category'].isin(cataegory)]

def get_under_stocked_products(products_df):
    return(products_df[products_df['stock_status']=='Understocked'])

def get_over_stocked_products(products_df):
    return(products_df[products_df['stock_status']=='Overstocked'])

def get_summary_kpi(products_df,sales_df):
    total_revenue = products_df['product_id'].apply(lambda product_id: get_revenue(products_df, sales_df, product_id)).sum()
    total_profit = products_df['profit'].sum()
    total_unit_sold = sales_df['quantity_sold'].sum()
    total_understocked_products = len(get_under_stocked_products(products_df))
    total_overstocked_products = len(get_over_stocked_products(products_df))
    return{'Total Revenue(k)':int(total_revenue/1e3),'Total Profit(k)':int(total_profit/1e3),'Total Unit Sold':int(total_unit_sold/1e3),'Total Understocked Products(k)':int(total_understocked_products),'Total Overstocked Products(k)':int(total_overstocked_products)}

def add_business_analytics(products_df,sales_df,purchase_df):
    products_df['current_Stock']= products_df['product_id'].apply(lambda product_id: get_current_stock(sales_df,purchase_df,product_id))
    products_df['profit']= products_df['product_id'].apply(lambda product_id:get_profit(products_df,sales_df,product_id))
    products_df['slow_moving']=products_df['product_id'].apply(lambda product_id: is_slow_moving(sales_df,product_id))
    products_df['stock_status']=products_df['product_id'].apply(lambda product_id:get_stock_status(products_df,product_id))
    return products_df,sales_df,purchase_df
