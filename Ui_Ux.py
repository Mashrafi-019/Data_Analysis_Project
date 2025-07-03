import streamlit as st
from b_analytics import *
import plotly.express as px
import numpy as np
import base64

st.set_page_config(page_title='Business Dashboard',layout='wide')

def upload_files():
    uploaded_files=st.sidebar.file_uploader(label='Upload CSV Files',type='csv',accept_multiple_files=True)
    products_df ,sales_df ,purchase_df = None,None,None

    for files in uploaded_files:
        if files.name =='products.csv' :
            products_df=pd.read_csv(files)
        elif files.name =='sales.csv':
            sales_df= pd.read_csv(files)
            sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date']).dt.date
        elif files.name =='purchases.csv':
            purchase_df=pd.read_csv(files)
    return products_df,sales_df,purchase_df
products_df,sales_df,purchase_df = upload_files()

st.sidebar.header('Filters')

date1=datetime.strptime('2024-01-01','%Y-%m-%d')
date2=datetime.strptime('2024-12-31','%Y-%m-%d')

date_range = st.sidebar.date_input(label='Select Date Range',value=[date1,date2])
category_filters = st.sidebar.multiselect(label ='Select Product Category',options=['Groceries','Electronics','Clothing','Perishables'])
location_filters = st.sidebar.multiselect(label='Select Location',options=['Dhaka','Chittagong','Sylhet','Rajshahi'],default=['Dhaka'])

st.header("Business Dashboard")
if products_df is not None and sales_df is not None and purchase_df is not None:
    products_df, sales_df, purchase_df = add_business_analytics(products_df, sales_df, purchase_df)
    start_date= str(date_range[0])
    end_date= str(date_range[1])

    filtered_sales=get_sales_between_dates(
        sales_df = sales_df,
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date(),
        locations = location_filters
    )

    filtered_products= get_categories(
        products_df=products_df,
        cataegory=category_filters
    )

    understocked_products = get_under_stocked_products(
        products_df=filtered_products
    )

    overstocked_products = get_over_stocked_products(
        products_df=filtered_products
    )

    key_metrics = get_summary_kpi(sales_df=filtered_sales,products_df=filtered_products)

    revenue_col, profit_col, units_sold_col, low_stock_col,high_stock_col = st.columns(5)
    with revenue_col:
        st.metric(
            label='Total Revenue(K)',
            value=f"{key_metrics['Total Revenue(k)']}"

        )
    with profit_col:
        st.metric(
            label='Total Profit(K)',
            value=f"{key_metrics['Total Profit(k)']}"
        )
    with units_sold_col:
        st.metric(
            label='Total Unit Sold(K)',
            value=f'{key_metrics['Total Unit Sold']}'

        )
    with low_stock_col:
        st.metric(
            label='Total Low stocked Products',
            value=f"{key_metrics['Total Understocked Products(k)']}"
        )
    with high_stock_col:
        st.metric(
            label = "Total Over stocked Products",
            value=f"{key_metrics['Total Overstocked Products(k)']}"
        )

    st.subheader('Top 10 Products by Profit')
    top_products = filtered_products.nlargest(10, 'profit')[['product_name', 'profit']]
    plot1 = px.bar(top_products, x='product_name', y='profit', title="Top 10 Products by Profit",color = 'product_name')
    st.plotly_chart(plot1,use_container_width=True)

    st.subheader('Profit by Categories')
    category_profit = filtered_products.groupby('category')['profit'].sum().reset_index()
    plot3 = px.pie(category_profit, values='profit', names='category', title="Profit Distribution by Category")
    st.plotly_chart(plot3,use_container_width=True)

    st.subheader("Product Stock and Profit Summary")
    summary_df = filtered_products[
        ['product_name', 'category', 'current_Stock', 'reorder_level', 'profit', 'stock_status']]
    summary_df['stock_status'] = summary_df['stock_status'].map({
        'Properly Stocked': '<span style="color:green">Properly Stocked</span>',
        'Understocked': '<span style="color:red">Understocked</span>',
        'Overstocked': '<span style="color:orange">Overstocked</span>'
    })
    st.markdown(summary_df.to_html(escape=False), unsafe_allow_html=True)

    st.subheader('Overstocked and Understocked Products')
    stock_issues = filtered_products[filtered_products['stock_status'].isin(['Understocked', 'Overstocked'])]
    stock_issues = stock_issues[['product_name', 'category', 'current_Stock', 'reorder_level', 'profit', 'stock_status']]
    stock_issues['suggested_reorder'] = np.where(stock_issues['stock_status'] == 'Understocked',
                                                 stock_issues['reorder_level'] - stock_issues['current_Stock'], 0)
    st.markdown(stock_issues.to_html(escape=False), unsafe_allow_html=True)


    def get_table_download_link(df, filename):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        return f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download {filename}</a>'
    st.markdown(get_table_download_link(summary_df, "product_summary"), unsafe_allow_html=True)
    st.markdown(get_table_download_link(stock_issues, "stock_issues"), unsafe_allow_html=True)

    st.subheader("Business Recommendations")
    recommendations = []
    # Restock or discontinue
    understocked = filtered_products[filtered_products['stock_status'] == 'Understocked']
    if not understocked.empty:
        recommendations.append(
            f"**Restock Urgently**: {len(understocked)} products are understocked. Prioritize restocking {understocked['product_name'].iloc[:2].to_list()}.")
    slow_moving_products = filtered_products[filtered_products['slow_moving']]
    if not slow_moving_products.empty:
        recommendations.append(
            f"**Consider Discontinuing**: {len(slow_moving_products)} slow-moving products (e.g., {slow_moving_products['product_name'].iloc[:2].to_list()}) have low sales.")

    # Inventory strategy
    overstocked = filtered_products[filtered_products['stock_status'] == 'Overstocked']
    if not overstocked.empty:
        recommendations.append(
            f"**Clear Overstock**: {len(overstocked)} products are overstocked. Consider promotions for {overstocked['product_name'].iloc[:2].to_list()} to reduce inventory costs.")
    recommendations.append(
        "**Inventory Strategy**: Implement just-in-time restocking for perishables and high-demand items to minimize waste and improve ROI.")

    for rec in recommendations:
        st.markdown(f"- {rec}")