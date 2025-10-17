# Labor Dynamics Analysis: College Enrollment vs Employment Trends

A comprehensive analysis of the relationship between college enrollment patterns and labor market employment dynamics in the United States.

## 📊 Project Overview

This project examines the complex interplay between higher education participation and labor market outcomes, providing insights into:

- **Educational Migration Patterns**: How college enrollment trends impact regional workforce development
- **Skills Gap Analysis**: Alignment between educational programs and labor market demands
- **Economic Impact Assessment**: The relationship between education investment and employment outcomes
- **Policy Implications**: Data-driven insights for education and workforce policy decisions

## 🎯 Research Questions

1. **How do college enrollment trends correlate with regional employment patterns?**
2. **What is the relationship between degree completion rates and employment outcomes?**
3. **How do economic cycles impact the college enrollment vs. direct employment decision?**
4. **What industries show the strongest correlation with specific educational programs?**
5. **How do demographic factors influence the education-employment pathway?**

## 📈 Key Analyses

### Core Analysis Modules
- **Trend Analysis**: Historical patterns in enrollment and employment data
- **Correlation Studies**: Statistical relationships between education and employment metrics
- **Geographic Analysis**: Regional variations and migration patterns
- **Demographic Segmentation**: Analysis by age, gender, socioeconomic factors
- **Industry Mapping**: Education-to-career pathway analysis

### Advanced Analytics
- **Predictive Modeling**: Forecasting enrollment and employment trends
- **Time Series Analysis**: Seasonal and cyclical pattern identification
- **Regression Analysis**: Causal relationship exploration
- **Clustering Analysis**: Identifying similar regions/demographics patterns

## 🗂️ Project Structure

```
labor-dynamics-analysis/
├── data/
│   ├── raw/              # Original, unprocessed datasets
│   ├── processed/        # Cleaned and transformed data
│   └── external/         # Third-party data sources
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_enrollment_analysis.ipynb
│   ├── 03_employment_trends.ipynb
│   ├── 04_correlation_analysis.ipynb
│   └── 05_predictive_modeling.ipynb
├── src/
│   ├── data_collection/  # Data gathering and API interfaces
│   ├── analysis/         # Core analysis functions
│   └── visualization/    # Plotting and dashboard utilities
├── config/               # Configuration files and parameters
├── tests/               # Unit tests and validation
├── docs/                # Documentation and methodology
└── reports/             # Generated analysis reports
```

## 📊 Data Sources

### Primary Data Sources
- **National Center for Education Statistics (NCES)**: College enrollment data
- **Bureau of Labor Statistics (BLS)**: Employment and unemployment statistics
- **Census Bureau**: Demographic and economic indicators
- **Federal Reserve Economic Data (FRED)**: Economic indicators

### Data Coverage
- **Time Period**: 2000-2024 (varies by dataset)
- **Geographic Scope**: National, state, and metropolitan statistical area levels
- **Demographics**: Age, gender, race/ethnicity, income levels
- **Education Levels**: Associate, bachelor's, graduate degrees by field

## 🛠️ Installation & Setup

### Prerequisites
```bash
Python 3.8+
Git
```

### Installation
```bash
# Clone the repository
git clone https://github.com/kamrawr/labor-dynamics-analysis.git
cd labor-dynamics-analysis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Configuration
```bash
# Copy sample configuration
cp config/config.sample.yaml config/config.yaml

# Edit configuration with your API keys and preferences
# Required: BLS API key, Census API key (optional but recommended)
```

## 🚀 Quick Start

### 1. Data Collection
```python
from src.data_collection import fetch_enrollment_data, fetch_employment_data

# Fetch latest data
enrollment_data = fetch_enrollment_data(years=range(2015, 2025))
employment_data = fetch_employment_data(years=range(2015, 2025))
```

### 2. Basic Analysis
```python
from src.analysis import correlation_analysis, trend_analysis

# Run correlation analysis
results = correlation_analysis(enrollment_data, employment_data)

# Generate trend reports
trends = trend_analysis(data_range='2015-2024')
```

### 3. Visualization
```python
from src.visualization import create_dashboard, plot_trends

# Create interactive dashboard
dashboard = create_dashboard(results)

# Generate trend plots
plot_trends(enrollment_data, employment_data, save_path='reports/')
```

## 📋 Usage Examples

### Running Analysis Notebooks
```bash
# Start Jupyter
jupyter lab

# Open notebooks in order:
# 01_data_exploration.ipynb - Initial data review
# 02_enrollment_analysis.ipynb - College enrollment trends
# 03_employment_trends.ipynb - Labor market analysis
# 04_correlation_analysis.ipynb - Relationship analysis
# 05_predictive_modeling.ipynb - Forecasting models
```

### Command Line Tools
```bash
# Update all datasets
python src/data_collection/update_data.py

# Run full analysis pipeline
python src/analysis/run_analysis.py --config config/config.yaml

# Generate reports
python src/reports/generate_report.py --type summary --output reports/
```

## 📊 Key Findings & Insights

> **Note**: This section will be populated as analysis progresses. Initial findings will focus on:
> - National enrollment trends (2015-2024)
> - Employment pattern correlations
> - Regional variation analysis
> - Economic impact assessment

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 src/ tests/
black src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Education Data Analysis Tools](https://github.com/topics/education-data)
- [Labor Market Analytics](https://github.com/topics/labor-market)
- [Economic Research Tools](https://github.com/topics/economic-research)

## 📧 Contact

- **Author**: kamrawr
- **Email**: rawrdog92@yahoo.com
- **GitHub**: [@kamrawr](https://github.com/kamrawr)

## 🙏 Acknowledgments

- National Center for Education Statistics for comprehensive education data
- Bureau of Labor Statistics for employment and economic indicators
- Open source community for excellent data analysis tools

---

**Last Updated**: October 2024  
**Version**: 0.1.0-dev
