# Marketing A/B Testing with Agentic Architecture

An intelligent A/B testing system that simulates how different consumer personas react to marketing images using LangGraph and OpenAI's vision capabilities.

## Overview

This project implements a sophisticated agentic architecture for marketing A/B testing that simulates three distinct consumer personas:

- **Single Mother (Sarah)**: Budget-conscious, family-focused, prioritizes safety and value
- **Young Male (Jake)**: High-income, status-seeking, values instant gratification and social approval  
- **Elderly Retiree (Robert)**: Fixed income, values quality and necessity, prefers simplicity

## Architecture

The system uses LangGraph to orchestrate a multi-agent workflow:

1. **Image Analysis**: Uses OpenAI's vision model to analyze marketing images
2. **Persona Simulation**: Each persona agent evaluates the marketing content based on their unique characteristics
3. **A/B Testing**: Compares two variants and provides statistical analysis
4. **Results Analysis**: Generates insights and recommendations

## Features

- 🤖 **Agentic Architecture**: LangGraph-powered workflow with specialized persona agents
- 🔍 **Image Analysis**: AI-powered marketing image analysis using GPT-4 Vision
- 👥 **Persona Simulation**: Realistic consumer behavior modeling
- 📊 **A/B Testing**: Statistical comparison of marketing variants
- 💾 **Results Export**: JSON results with detailed analytics
- 🐳 **Containerized**: Docker support for easy deployment

## Installation

### Prerequisites

- Python 3.11+
- OpenAI API key
- Docker (optional)

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Agentic-AI-Experimentation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Docker Setup

1. Build the Docker image:
```bash
docker build -t ab-testing-agents .
```

2. Run with environment file:
```bash
docker run --env-file .env ab-testing-agents
```

## Usage

### Basic Usage

Run A/B test with a sample image:
```bash
python main.py
```

### Custom Image URL

Test with your own marketing image:
```bash
python main.py --image-url "https://your-image-url.com/image.jpg"
```

### Detailed Analysis

Get comprehensive persona responses:
```bash
python main.py --detailed
```

### Docker Usage

```bash
# Basic run
docker run --env-file .env ab-testing-agents

# Custom image with detailed output
docker run --env-file .env ab-testing-agents python main.py --image-url "https://example.com/image.jpg" --detailed

# Mount local results directory
docker run --env-file .env -v $(pwd)/results:/app/results ab-testing-agents
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEFAULT_IMAGE_URL`: Default image URL for testing
- `OUTPUT_DIR`: Directory for saving results (default: "results")

### Command Line Options

- `--image-url`: URL or path to marketing image
- `--output-dir`: Directory to save results
- `--detailed`: Show detailed persona responses
- `--save`: Save results to file (default: True)

## Project Structure

```
├── agents/
│   ├── __init__.py
│   └── personas.py          # Persona agent implementations
├── workflow/
│   ├── __init__.py
│   └── ab_testing_graph.py  # LangGraph workflow definition
├── utils/
│   ├── __init__.py
│   └── image_processor.py   # Image processing utilities
├── main.py                  # Main execution script
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── .env.example            # Environment template
└── README.md               # This file
```

## Persona Details

### Single Mother (Sarah)
- **Budget**: $200/month discretionary, max $100/purchase
- **Priorities**: Child safety, practical value, family benefits
- **Decision Factors**: Value for money, durability, necessity
- **Behavior**: Conservative, research-oriented, family-first

### Young Male (Jake)  
- **Budget**: $800/month discretionary, max $500/purchase
- **Priorities**: Status, instant gratification, social approval
- **Decision Factors**: Brand appeal, technology, performance
- **Behavior**: Impulsive, trend-following, self-focused

### Elderly Retiree (Robert)
- **Budget**: $150/month discretionary, max $75/purchase
- **Priorities**: Value, health benefits, simplicity
- **Decision Factors**: Quality, necessity, ease of use
- **Behavior**: Cautious, practical, health-conscious

## Sample Output

```
============================================================
           A/B TESTING RESULTS SUMMARY
============================================================

🏆 WINNER: Variant B
📊 Confidence Score: 15.33%
📈 Statistical Significance: Yes

📋 OVERALL SCORES:
   Variant A Average: 42.67%
   Variant B Average: 58.00%

👥 PERSONA ANALYSIS:

   Single Mother:
     • Preferred Variant: B
     • Variant A Score: 35.00%
     • Variant B Score: 65.00%
     • Difference: 30.00%

💡 RECOMMENDATIONS:
   1. Variant B performs better overall with 15.33% higher conversion
   2. Single Mother strongly prefers Variant B (difference: 30.00%)
   3. Focus on emotional appeals for better conversion rates
```

## API Integration

The system is designed for easy integration into marketing workflows:

```python
from workflow.ab_testing_graph import ABTestingWorkflow

workflow = ABTestingWorkflow(api_key="your-key")
results = await workflow.run_ab_test(initial_state)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Security

- Environment variables are used for API keys
- Non-root Docker user for container security
- Input validation for image URLs and file paths

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your API key is set in the `.env` file
2. **Image URL Invalid**: Verify the image URL is accessible and points to an image
3. **Docker Permission Issues**: Ensure Docker daemon is running and you have permissions

### Support

For issues and questions:
- Check the existing GitHub issues
- Create a new issue with detailed description
- Include error logs and environment details

## Future Enhancements

- Web interface for easier testing
- Additional persona types
- Integration with marketing platforms
- Real-time A/B testing capabilities
- Advanced statistical analysis
