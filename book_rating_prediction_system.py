"""
Book Rating Prediction System
Predicts book ratings using metadata and review sentiment analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def generate_book_dataset(n_samples=500, random_state=42):
    """Generate synthetic book dataset with metadata and ratings"""
    np.random.seed(random_state)
    
    genres = ['Fiction', 'Mystery', 'Romance', 'Science Fiction', 'Fantasy', 'Biography', 'History', 'Self-Help']
    authors = [f'Author_{i}' for i in range(1, 51)]
    publishers = [f'Publisher_{i}' for i in range(1, 21)]
    
    data = []
    for i in range(n_samples):
        genre = np.random.choice(genres)
        author_id = np.random.randint(1, 51)
        publisher_id = np.random.randint(1, 21)
        pages = np.random.randint(100, 800)
        publication_year = np.random.randint(2000, 2024)
        num_reviews = np.random.randint(10, 5000)
        
        # Sentiment score (0-1)
        sentiment_score = np.random.uniform(0.3, 0.95)
        
        # Calculate rating based on features
        base_rating = 3.0
        base_rating += sentiment_score * 2.0  # Sentiment contributes up to 2 points
        base_rating += (pages / 800) * 0.5  # Longer books slightly higher
        base_rating += (num_reviews / 5000) * 0.5  # More reviews slightly higher
        base_rating += np.random.normal(0, 0.3)  # Add noise
        
        rating = np.clip(base_rating, 1.0, 5.0)
        
        data.append({
            'Book_ID': f'B{i:04d}',
            'Genre': genre,
            'Author_ID': author_id,
            'Publisher_ID': publisher_id,
            'Pages': pages,
            'Publication_Year': publication_year,
            'Num_Reviews': num_reviews,
            'Sentiment_Score': sentiment_score,
            'Rating': rating
        })
    
    df = pd.DataFrame(data)
    return df

def prepare_features(df):
    """Prepare features for modeling"""
    df_copy = df.copy()
    
    # Encode categorical variables
    le_genre = LabelEncoder()
    df_copy['Genre_Encoded'] = le_genre.fit_transform(df_copy['Genre'])
    
    # Select features
    feature_cols = ['Genre_Encoded', 'Author_ID', 'Publisher_ID', 'Pages', 
                   'Publication_Year', 'Num_Reviews', 'Sentiment_Score']
    
    X = df_copy[feature_cols]
    y = df_copy['Rating']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    return X_scaled, y, scaler, le_genre

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple rating prediction models"""
    models = {}
    results = []
    
    # Linear Regression
    print("Training Linear Regression...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    
    models['Linear Regression'] = lr
    results.append({
        'Model': 'Linear Regression',
        'MAE': mean_absolute_error(y_test, y_pred_lr),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
        'R2_Score': r2_score(y_test, y_pred_lr)
    })
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    
    models['Random Forest'] = rf
    results.append({
        'Model': 'Random Forest',
        'MAE': mean_absolute_error(y_test, y_pred_rf),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'R2_Score': r2_score(y_test, y_pred_rf)
    })
    
    # Gradient Boosting
    print("Training Gradient Boosting...")
    gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    
    models['Gradient Boosting'] = gb
    results.append({
        'Model': 'Gradient Boosting',
        'MAE': mean_absolute_error(y_test, y_pred_gb),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'R2_Score': r2_score(y_test, y_pred_gb)
    })
    
    return models, pd.DataFrame(results), y_pred_rf

def plot_rating_distribution(df):
    """Plot rating distribution"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].hist(df['Rating'], bins=30, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Rating', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0].set_title('Book Rating Distribution', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    # Box plot
    axes[1].boxplot(df['Rating'], vert=True)
    axes[1].set_ylabel('Rating', fontsize=11, fontweight='bold')
    axes[1].set_title('Rating Box Plot', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_rating_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: book_rating_distribution.png")
    plt.close()

def plot_model_comparison(results_df):
    """Plot model performance comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # MAE comparison
    axes[0].bar(results_df['Model'], results_df['MAE'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_ylabel('MAE', fontsize=11, fontweight='bold')
    axes[0].set_title('Mean Absolute Error', fontsize=12, fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(results_df['MAE']):
        axes[0].text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    
    # RMSE comparison
    axes[1].bar(results_df['Model'], results_df['RMSE'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_ylabel('RMSE', fontsize=11, fontweight='bold')
    axes[1].set_title('Root Mean Squared Error', fontsize=12, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    for i, v in enumerate(results_df['RMSE']):
        axes[1].text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
    
    # R2 Score comparison
    axes[2].bar(results_df['Model'], results_df['R2_Score'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[2].set_ylabel('R² Score', fontsize=11, fontweight='bold')
    axes[2].set_title('R² Score Comparison', fontsize=12, fontweight='bold')
    axes[2].grid(axis='y', alpha=0.3)
    axes[2].set_ylim([0, 1.1])
    for i, v in enumerate(results_df['R2_Score']):
        axes[2].text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: book_model_comparison.png")
    plt.close()

def plot_predictions_vs_actual(y_test, y_pred):
    """Plot predictions vs actual values"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].scatter(y_test, y_pred, alpha=0.6, color='#3498db', edgecolor='black', linewidth=0.5)
    axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0].set_xlabel('Actual Rating', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Predicted Rating', fontsize=11, fontweight='bold')
    axes[0].set_title('Predictions vs Actual (Random Forest)', fontsize=12, fontweight='bold')
    axes[0].grid(alpha=0.3)
    
    # Residuals
    residuals = y_test - y_pred
    axes[1].scatter(y_pred, residuals, alpha=0.6, color='#e74c3c', edgecolor='black', linewidth=0.5)
    axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
    axes[1].set_xlabel('Predicted Rating', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Residuals', fontsize=11, fontweight='bold')
    axes[1].set_title('Residual Plot', fontsize=12, fontweight='bold')
    axes[1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_predictions_vs_actual.png', dpi=300, bbox_inches='tight')
    print("Saved: book_predictions_vs_actual.png")
    plt.close()

def plot_feature_importance(models):
    """Plot feature importance"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    feature_names = ['Genre', 'Author_ID', 'Publisher_ID', 'Pages', 'Pub_Year', 'Num_Reviews', 'Sentiment']
    
    # Random Forest
    rf = models['Random Forest']
    importance_rf = pd.DataFrame({
        'Feature': feature_names,
        'Importance': rf.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    axes[0].barh(importance_rf['Feature'], importance_rf['Importance'], 
                color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest - Feature Importance', fontsize=12, fontweight='bold')
    axes[0].invert_yaxis()
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gradient Boosting
    gb = models['Gradient Boosting']
    importance_gb = pd.DataFrame({
        'Feature': feature_names,
        'Importance': gb.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    axes[1].barh(importance_gb['Feature'], importance_gb['Importance'],
                color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1].set_title('Gradient Boosting - Feature Importance', fontsize=12, fontweight='bold')
    axes[1].invert_yaxis()
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: book_feature_importance.png")
    plt.close()

def plot_rating_by_genre(df):
    """Plot rating distribution by genre"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Box plot
    genre_order = df.groupby('Genre')['Rating'].median().sort_values(ascending=False).index
    df_sorted = df.copy()
    df_sorted['Genre'] = pd.Categorical(df_sorted['Genre'], categories=genre_order, ordered=True)
    
    sns.boxplot(data=df_sorted, x='Genre', y='Rating', ax=axes[0], palette='Set2')
    axes[0].set_xlabel('Genre', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Rating', fontsize=11, fontweight='bold')
    axes[0].set_title('Rating Distribution by Genre', fontsize=12, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y', alpha=0.3)
    
    # Average rating
    avg_rating = df.groupby('Genre')['Rating'].mean().sort_values(ascending=False)
    axes[1].bar(avg_rating.index, avg_rating.values, color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Genre', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Average Rating', fontsize=11, fontweight='bold')
    axes[1].set_title('Average Rating by Genre', fontsize=12, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_rating_by_genre.png', dpi=300, bbox_inches='tight')
    print("Saved: book_rating_by_genre.png")
    plt.close()

def plot_sentiment_correlation(df):
    """Plot sentiment score vs rating correlation"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].scatter(df['Sentiment_Score'], df['Rating'], alpha=0.6, color='#9b59b6', edgecolor='black', linewidth=0.5)
    z = np.polyfit(df['Sentiment_Score'], df['Rating'], 1)
    p = np.poly1d(z)
    axes[0].plot(df['Sentiment_Score'].sort_values(), p(df['Sentiment_Score'].sort_values()), 
                "r--", lw=2, label=f'Trend line')
    axes[0].set_xlabel('Sentiment Score', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Rating', fontsize=11, fontweight='bold')
    axes[0].set_title('Sentiment Score vs Book Rating', fontsize=12, fontweight='bold')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    # Correlation heatmap
    corr_data = df[['Pages', 'Publication_Year', 'Num_Reviews', 'Sentiment_Score', 'Rating']].corr()
    sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[1], 
               cbar_kws={'label': 'Correlation'}, vmin=-1, vmax=1)
    axes[1].set_title('Feature Correlation Matrix', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/book_sentiment_correlation.png', dpi=300, bbox_inches='tight')
    print("Saved: book_sentiment_correlation.png")
    plt.close()

def main():
    print("="*80)
    print("BOOK RATING PREDICTION SYSTEM")
    print("="*80)
    
    # Generate dataset
    print("\n[1] Generating synthetic book dataset...")
    df = generate_book_dataset(n_samples=500)
    df.to_csv('/home/ubuntu/book_data.csv', index=False)
    print(f"Dataset generated: {len(df)} books")
    print(f"Average rating: {df['Rating'].mean():.2f}")
    print(f"Rating range: {df['Rating'].min():.2f} - {df['Rating'].max():.2f}")
    
    # Prepare features
    print("\n[2] Preparing features...")
    X, y, scaler, le_genre = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Train models
    print("\n[3] Training rating prediction models...")
    models, results_df, y_pred_rf = train_models(X_train, X_test, y_train, y_test)
    results_df.to_csv('/home/ubuntu/book_model_results.csv', index=False)
    print("\nModel Results:")
    print(results_df.to_string(index=False))
    
    # Generate visualizations
    print("\n[4] Generating visualizations...")
    plot_rating_distribution(df)
    plot_model_comparison(results_df)
    plot_predictions_vs_actual(y_test, y_pred_rf)
    plot_feature_importance(models)
    plot_rating_by_genre(df)
    plot_sentiment_correlation(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
