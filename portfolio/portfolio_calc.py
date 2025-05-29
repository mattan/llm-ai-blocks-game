from flask import request, render_template, jsonify, redirect
import pandas as pd
from datetime import datetime, timedelta
import requests
import plotly.graph_objects as go
from cachetools.func import ttl_cache
import numpy as np

@ttl_cache  # ttl=600 maxsize=128
def get_yahoo_finance_data(ticker):
    """פונקציה פשוטה להורדת נתונים מ-Yahoo Finance"""
    end_date = int(datetime.now().timestamp())
    start_date = int((datetime.now() - timedelta(days=365)).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={start_date}&period2={end_date}&interval=1d"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # יצירת DataFrame
            df = pd.DataFrame({
                'Date': [datetime.fromtimestamp(ts) for ts in timestamps],
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })
            df.set_index('Date', inplace=True)
            return df,meta
        else:
            print(f"לא נמצאו נתונים עבור {ticker}")
            return None
            
    except Exception as e:
        print(f"שגיאה בהורדת נתונים עבור {ticker}: {str(e)}")
        return None


def calculate_shifted_data(ko_data, pep_data, shift_days=0):
    """מחשבת נתונים מוזזים עבור PEP"""
    returns = pd.DataFrame()
    returns['KO'] = ko_data['Close'].pct_change().dropna()
    
    # הזזת הנתונים של PEP לפי מספר הימים המבוקש
    if shift_days != 0:
        shifted_pep = pep_data['Close'].shift(shift_days)
    else:
        shifted_pep = pep_data['Close']
    
    returns['PEP'] = shifted_pep.pct_change().dropna()
    
    # חישוב שונות משותפת
    if len(returns) > 1:  # וודא שיש מספיק נקודות נתונים
        covariance = returns.corr().iloc[0, 1]
    else:
        covariance = 0
    
    return returns, covariance

def create_plot(ko_data, pep_data, shift_days=0, stock1_name='Stock 1', stock2_name='Stock 2'):
    """יצירת גרף אינטראקטיבי עם Plotly"""
    try:
        # יצירת עותק של הנתונים כדי לא לשנות את המקור
        ko_df = ko_data.copy()
        pep_df = pep_data.copy()
        
        # הזזת הנתונים של PEP לפי מספר הימים הנבחר
        if shift_days != 0:
            pep_df = pep_df.shift(shift_days)
        
        # יצירת הגרף
        fig = go.Figure()
        
        # הוספת קו למנייה הראשונה
        fig.add_trace(go.Scatter(
            x=ko_df.index,
            y=ko_df['Close'],
            mode='lines',
            name=stock1_name,
            line=dict(color='#1f77b4')
        ))
        
        # הוספת קו למנייה השנייה
        shift_text = f' (מוזז ב-{abs(shift_days)} ימים)' if shift_days != 0 else ''
        fig.add_trace(go.Scatter(
            x=pep_df.index,
            y=pep_df['Close'],
            mode='lines',
            name=f'{stock2_name}{shift_text}',
            line=dict(color='#ff7f0e')
        ))
        
        # עדכון עיצוב הגרף
        fig.update_layout(
            title=f'השוואת מניות {stock1_name} ו-{stock2_name}',
            xaxis_title='תאריך',
            yaxis_title='מחיר סגירה (USD)',
            hovermode='x',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.2)',
                borderwidth=1
            ),
            template='plotly_white',
            height=600,
            margin=dict(l=50, r=50, t=80, b=50),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        
        # המרת הגרף ל-HTML
        return fig.to_html(
            full_html=False,
            config={
                'displayModeBar': True,
                'scrollZoom': True,
                'displaylogo': False,
                'responsive': True
            }
        )
        
    except Exception as e:
        print(f"שגיאה ביצירת הגרף: {str(e)}")
        return "<div style='color: red; text-align: center; padding: 20px;'>אירעה שגיאה ביצירת הגרף. אנא נסה שוב מאוחר יותר.</div>"


def get_stock_info(ticker_meta):
    """מחזיר את שם המניה מתוך האובייקט meta"""
    if not ticker_meta:
        return {'name': 'Unknown', 'symbol': 'UNKNOWN', 'sector': 'N/A', 'industry': 'N/A'}
    
    return {
        'name': ticker_meta.get('shortName', ticker_meta.get('symbol', 'Unknown')),
        'symbol': ticker_meta.get('symbol', 'UNKNOWN'),
        'sector': ticker_meta.get('instrumentType', 'N/A'),
        'industry': ticker_meta.get('exchangeTimezoneName', 'N/A')
    }


def home():
    try:
        # Get parameters from URL or use defaults
        portf1 = request.args.get('portf1', 'KO').upper()
        portf2 = request.args.get('portf2', 'PEP').upper()
        

        # Fetch stock data and info
        ko_result = get_yahoo_finance_data(portf1)
        pep_result = get_yahoo_finance_data(portf2)
        
        if ko_result is None or pep_result is None:
            return "שגיאה בטעינת נתוני מניות. נסה שוב מאוחר יותר."
            
        ko_data, ko_meta = ko_result
        pep_data, pep_meta = pep_result

        # Get stock information
        stock1_info = get_stock_info(ko_meta or {})
        stock2_info = get_stock_info(pep_meta or {})

        # Handle shift_days parameter
        shift_param = request.args.get('shift_days', '0')
        
        # Check if we need to find optimal shift
        if str(shift_param).upper() == 'AUTO':
            optimal_shift = find_optimal_shift(ko_data, pep_data)
            return redirect(f'?portf1={portf1}&portf2={portf2}&shift_days={optimal_shift}')
            
        # Otherwise, try to convert to int
        try:
            shift_days = int(shift_param)
        except (ValueError, TypeError):
            shift_days = 0

        # Calculate data and create plot
        returns, covariance = calculate_shifted_data(ko_data, pep_data, shift_days)
        
        # יצירת הגרף עם שמות מלאים של המניות
        plot_html = create_plot(
            ko_data, 
            pep_data, 
            shift_days,
            stock1_name=f"{stock1_info['name']} ({stock1_info['symbol']})",
            stock2_name=f"{stock2_info['name']} ({stock2_info['symbol']})"
        )
        
        # תאריך עדכון אחרון
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template('stocks.html', 
                             plot_html=plot_html,
                             covariance=covariance,
                             current_time=current_time,
                             portf1=portf1,
                             portf2=portf2,
                             shift_days=shift_days,
                             stock1_info=stock1_info,
                             stock2_info=stock2_info)
    except Exception as e:
        error_msg = f"אירעה שגיאה: {str(e)}"
        print(error_msg)
        return render_template('error.html', error=error_msg)


def update_plot():
    try:
        # קבלת פרמטרים מה-URL
        portf1 = request.args.get('portf1', 'KO').upper()
        portf2 = request.args.get('portf2', 'PEP').upper()
        shift_days_param = int(request.args.get('shift_days', '0'))
        
        # טעינת נתוני המניות
        ko_data, _ = get_yahoo_finance_data(portf1)
        pep_data, _ = get_yahoo_finance_data(portf2)

        
        print(f"Received request - Portf1: {portf1}, Portf2: {portf2}, Shift Days: {shift_days}")
        
        # טעינת נתוני מניות
        ko_data = get_yahoo_finance_data(portf1)
        pep_data = get_yahoo_finance_data(portf2)
        
        print(f"Loaded data - {portf1}: {len(ko_data) if ko_data is not None else 0} rows, {portf2}: {len(pep_data) if pep_data is not None else 0} rows")
        
        if ko_data is None or pep_data is None:
            error_msg = 'Failed to load stock data - missing data'
            print(error_msg)
            return jsonify({
                'error': error_msg,
                'plot_html': '<div style="color: red; padding: 20px; text-align: center;">שגיאה בטעינת נתוני המניות. נסה לרענן את הדף.</div>',
                'covariance': 0
            }), 200
        
        try:
            # קבלת מידע נוסף על המניות
            stock1_info = get_stock_info(portf1)
            stock2_info = get_stock_info(portf2)
            
            # חישוב נתונים מוזזים
            returns, covariance = calculate_shifted_data(ko_data, pep_data, shift_days)
            print(f"Calculated covariance: {covariance}")
            
            # יצירת גרף מעודכן עם שמות מלאים
            plot_html = create_plot(
                ko_data, 
                pep_data, 
                shift_days,
                stock1_name=f"{stock1_info['name']} ({stock1_info['symbol']})",
                stock2_name=f"{stock2_info['name']} ({stock2_info['symbol']})"
            )
            
            response = {
                'plot_html': plot_html,
                'covariance': float(covariance) if not pd.isna(covariance) else 0,
                'stock1_info': {
                    'name': stock1_info['name'],
                    'symbol': stock1_info['symbol'],
                    'sector': stock1_info['sector'],
                    'industry': stock1_info['industry']
                },
                'stock2_info': {
                    'name': stock2_info['name'],
                    'symbol': stock2_info['symbol'],
                    'sector': stock2_info['sector'],
                    'industry': stock2_info['industry']
                }
            }
            print("Returning successful response")
            return jsonify(response)
            
        except Exception as e:
            error_msg = f'Error in plot generation: {str(e)}'
            print(error_msg)
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': error_msg,
                'plot_html': f'<div style="color: red; padding: 20px; text-align: center;">שגיאה ביצירת הגרף: {str(e)}</div>',
                'covariance': 0
            }), 500
            
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': error_msg,
            'plot_html': '<div style="color: red; padding: 20px; text-align: center;">אירעה שגיאה בלתי צפויה. נסה לרענן את הדף.</div>',
            'covariance': 0
        }), 500


####################################

def find_optimal_shift(stock1_data, stock2_data):
    """
    מוצא את ההזזה האופטימלית בין שתי מניות
    מחזיר את מספר הימים האופטימלי להזזה
    """
    try:
        # Define search ranges (exclude 0)
        negative_shifts = range(-30, 0)  # -30 to -1
        positive_shifts = range(1, 31)   # 1 to 30
        
        # Combine both ranges without 0
        shift_ranges = list(negative_shifts) + list(positive_shifts)
        correlations = []
        
        # Calculate correlation for each shift
        for shift in shift_ranges:
            _, corr = calculate_shifted_data(stock1_data, stock2_data, shift)
            correlations.append(abs(corr))  # Use absolute value to find maximum correlation
        
        # Find the shift with maximum correlation
        optimal_shift = shift_ranges[np.argmax(correlations)]
        
        return optimal_shift
        
    except Exception as e:
        print(f"Error in find_optimal_shift: {str(e)}")
        return 0  # Return 0 as default in case of error
