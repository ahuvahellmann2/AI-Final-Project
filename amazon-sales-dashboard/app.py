import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & TITLE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("Amazon Category Analysis Dashboard")
st.markdown("""
This dashboard explores information about Amazon product categories including amount of products, discounts, and ratings.
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. DATA LOADING & CLEANING (Exact logic from notebook)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('amazon-sales-dashboard/data/raw/amazon.csv')
    except FileNotFoundError:
        data = pd.read_csv('data/raw/amazon.csv')
    
    # Clean and convert 'discounted_price'
    data['discounted_price'] = data['discounted_price'].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
    data['discounted_price'] = pd.to_numeric(data['discounted_price'], errors='coerce')

    # Clean and convert 'actual_price'
    data['actual_price'] = data['actual_price'].astype(str).str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
    data['actual_price'] = pd.to_numeric(data['actual_price'], errors='coerce')

    # Clean and convert 'discount_percentage'
    data['discount_percentage'] = data['discount_percentage'].astype(str).str.replace('%', '', regex=False)
    data['discount_percentage'] = pd.to_numeric(data['discount_percentage'], errors='coerce')

    # Clean and convert 'rating'
    data['rating'] = pd.to_numeric(data['rating'], errors='coerce')

    # Clean and convert 'rating_count'
    data['rating_count'] = data['rating_count'].astype(str).str.replace(',', '', regex=False)
    data['rating_count'] = pd.to_numeric(data['rating_count'], errors='coerce')

    # Drop specified columns
    columns_to_drop = ['img_link', 'product_link', 'about_product', 'review_id', 'review_content']
    data = data.drop(columns=columns_to_drop, errors='ignore')

    # Extract main category
    data['main_category'] = data['category'].apply(lambda x: x.split('|')[0].strip() if pd.notnull(x) else x)

    return data

data = load_data()

# -----------------------------------------------------------------------------
# 3. INTERACTIVE SIDEBAR FILTER
# -----------------------------------------------------------------------------
st.sidebar.header("Filter Options")
categories = ["All"] + sorted([cat for cat in data['main_category'].dropna().unique()])
selected_category = st.sidebar.selectbox("Select Primary Category:", categories)

filtered_data = data if selected_category == "All" else data[data['main_category'] == selected_category]

# -----------------------------------------------------------------------------
# 4. SUMMARY METRICS
# -----------------------------------------------------------------------------
st.subheader("Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Products", f"{len(filtered_data):,}")
col2.metric("Average Discounted Price", f"₹{filtered_data['discounted_price'].mean():,.2f}")
col3.metric("Average Discount Depth", f"{filtered_data['discount_percentage'].mean():.1f}%")
col4.metric("Average Customer Rating", f"{filtered_data['rating'].mean():.2f} / 5.0")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. VISUAL ANALYTICS & DIRECT QUESTIONS
# -----------------------------------------------------------------------------
st.subheader("Visual Analytics & Summary Tables")

# -----------------------------------------------------------------------------
# QUESTION 1: Which category has the most products?
# -----------------------------------------------------------------------------
st.markdown("## 1. Which category has the most products?")

product_count = filtered_data['main_category'].value_counts().head(10).reset_index()
product_count.columns = ['Main Category', 'Product Count']

# Chart
fig1 = px.bar(
    product_count,
    x='Product Count',
    y='Main Category',
    orientation='h',
    title="Top 10 Categories by Number of Products",
    labels={'Product Count': 'Number of Products', 'Main Category': 'Category'},
    color='Product Count',
    color_continuous_scale='tealgrn'  
)
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

st.dataframe(product_count, use_container_width=True)

st.info("""
** Majority of products belong to the Electronics category, followed closely by Computers&Accessories and Home&Kitchen). 
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# QUESTION 2: Which categories have the highest ratings vs. highest discounts?
# -----------------------------------------------------------------------------
st.markdown("## 2. Which categories have the highest ratings and highest discounts?")

avg_rating = filtered_data.groupby('main_category')['rating'].mean().dropna()
avg_discount = filtered_data.groupby('main_category')['discount_percentage'].mean().dropna()

top_ratings = avg_rating.sort_values(ascending=False).head(10).reset_index()
top_ratings.columns = ['Main Category', 'Average Rating']

top_discounts = avg_discount.sort_values(ascending=False).head(10).reset_index()
top_discounts.columns = ['Main Category', 'Average Discount Percentage (%)']

col_a, col_b = st.columns(2)

with col_a:
    fig_rating = px.bar(
        top_ratings,
        x='Average Rating',
        y='Main Category',
        orientation='h',
        title="Top 10 Categories by Average Rating",
        color='Average Rating',
        color_continuous_scale='viridis'
    )
    fig_rating.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_range=[3.0, 5.0])
    st.plotly_chart(fig_rating, use_container_width=True)
    
    st.markdown("**Top 10 Categories by Average Rating:**")
    st.dataframe(top_ratings.style.format({'Average Rating': '{:.2f}'}), use_container_width=True)

with col_b:
    fig_discount = px.bar(
        top_discounts,
        x='Average Discount Percentage (%)',
        y='Main Category',
        orientation='h',
        title="Top 10 Categories by Average Discount %",
        color='Average Discount Percentage (%)',
        color_continuous_scale='magma'
    )
    fig_discount.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_discount, use_container_width=True)
    
    st.markdown("**Top 10 Categories by Average Discount %:**")
    st.dataframe(top_discounts.style.format({'Average Discount Percentage (%)': '{:.2f}%'}), use_container_width=True)

st.info("""
**The Office Products and Toys & Games categories sit highest on the customer ratings chart, while in contrast, they have the lowest discounts.**
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# 'Further Analysis': Category Performance Scatter Plot (Rating vs. Discount Depth)
# -----------------------------------------------------------------------------
st.markdown("# 3. Seeing that categories with the highest ratings also had the lowest discounts drew me to explore whether there is a real relationship between discounts and ratings")

category_performance = pd.DataFrame({
    'Average Rating': avg_rating,
    'Average Discount Percentage (%)': avg_discount
}).dropna().reset_index().rename(columns={'main_category': 'Main Category'})

fig_scatter = px.scatter(
    category_performance,
    x='Average Discount Percentage (%)',
    y='Average Rating',
    color='Main Category',
    title='Average Rating vs. Average Discount Percentage by Category',
    labels={
        'Average Discount Percentage (%)': 'Average Discount Percentage (%)',
        'Average Rating': 'Average Rating',
        'Main Category': 'Category'
    }
)
fig_scatter.update_traces(marker=dict(size=12))
fig_scatter.update_layout(yaxis_range=[3.0, 5.0])
st.plotly_chart(fig_scatter, use_container_width=True)

st.dataframe(
    category_performance.style.format({
        'Average Rating': '{:.2f}', 
        'Average Discount Percentage (%)': '{:.2f}%'
    }), 
    use_container_width=True
)



category_performance_sorted = category_performance.sort_values(by='Average Discount Percentage (%)', ascending=False)

fig_dual = go.Figure()

# Bar Chart for Discount Percentage
fig_dual.add_trace(
    go.Bar(
        x=category_performance_sorted['Main Category'],
        y=category_performance_sorted['Average Discount Percentage (%)'],
        name='Avg Discount (%)',
        marker_color='#2ca02c',
        yaxis='y'
    )
)

# Line Chart for Average Rating
fig_dual.add_trace(
    go.Scatter(
        x=category_performance_sorted['Main Category'],
        y=category_performance_sorted['Average Rating'],
        name='Avg Rating',
        mode='lines+markers',
        line=dict(color='red', width=3),
        marker=dict(size=8),
        yaxis='y2'
    )
)

fig_dual.update_layout(
    title="Average Rating and Discount Percentage by Category (Sorted by Discount)",
    xaxis=dict(title="Main Category", tickangle=45),
    yaxis=dict(title="Average Discount Percentage (%)", range=[0, 100], title_font=dict(color="green"), tickfont=dict(color="green")),
    yaxis2=dict(title="Average Rating", range=[3.0, 5.0], overlaying='y', side='right', title_font=dict(color="red"), tickfont=dict(color="red")),
    legend=dict(x=1.05, y=1)
)

st.plotly_chart(fig_dual, use_container_width=True)

st.markdown("**Categories Sorted by Highest Average Discount Percentage:**")
st.dataframe(
    category_performance_sorted.style.format({
        'Average Rating': '{:.2f}', 
        'Average Discount Percentage (%)': '{:.2f}%'
    }), 
    use_container_width=True
)

st.info("""
** Although at a glance, the previous charts seemed to show a negative correlation between discount and ratings, 
this analysis did not show any significant relationship between the two variables. Furthermore, although the top 3 categories dominated
the rest of the categories, they were not high up on either chart. This suggests that the relationship between discount and ratings is not as straightforward as it may seem.
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. DATA PREVIEW TABLE
# -----------------------------------------------------------------------------
st.subheader("Full Dataset Preview")
st.dataframe(
    filtered_data[[
        'product_id', 'product_name', 'main_category', 
        'actual_price', 'discounted_price', 
        'discount_percentage', 'rating', 'rating_count'
    ]].head(20),
    use_container_width=True
)