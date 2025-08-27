# Chispart Mobile Architecture

## Overview

Chispart Mobile is a Progressive Web App (PWA) designed to provide a universal interface for interacting with various AI APIs, with special optimizations for mobile devices and Termux on Android.

## Core Components

### 1. API Key Management

- **Location**: `core/api_key_manager.py`
- **Responsibilities**:
  - Secure storage of API keys using AES-256 encryption
  - Key derivation using Fernet
  - Environment variable support
  - Interactive setup process

### 2. Configuration System

- **Location**: `core/config_manager.py`
- **Responsibilities**:
  - Multilevel configuration system (user, system, defaults)
  - Environment variable integration
  - Configuration validation
  - Mobile optimizations

### 3. PWA Functionality

- **Location**: `core/pwa_manager.py`
- **Responsibilities**:
  - Service worker implementation
  - Offline caching strategy
  - Background sync
  - Push notifications

### 4. Main Application

- **Location**: `app.py`
- **Responsibilities**:
  - Flask application setup
  - Route management
  - Template rendering
  - Mobile-specific optimizations

## Mobile Optimizations

- Termux environment detection
- Adjusted timeouts for mobile connections
- Reduced file size limits
- Compact UI components

## Integration Points

- **Blackbox AI API**: Primary AI interaction
- **OpenAI, Anthropic, Groq, Together AI**: Additional API support
- **Termux**: Special mobile environment support

## Security Considerations

- AES-256 encryption for API key storage
- Secure handling of sensitive data
- Environment variable support

## Deployment

- Docker support for containerization
- Environment-specific configurations
- Mobile-specific build processes

## Next Steps

1. Complete frontend template and asset creation
2. Implement code linting and unit tests
3. Generate comprehensive documentation
4. Integrate cloud components with mobile systems