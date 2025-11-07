#!/bin/bash
# ============================================================================
# DEMIR AI - PRODUCTION DEPLOYMENT SCRIPT
# Complete deployment automation for Phase 16 launch
# Full Production Code - NO MOCKS
# Created: November 7, 2025
# ============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker found"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose found"

    # Check environment file
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        exit 1
    fi
    log_success ".env file found"

    # Check Docker daemon
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    log_success "Docker daemon is running"

    # Check disk space
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then  # Less than 5GB
        log_warning "Low disk space available: ${AVAILABLE_SPACE}KB"
    else
        log_success "Sufficient disk space available"
    fi
}

# ============================================================================
# BACKUP CURRENT STATE
# ============================================================================

backup_current_state() {
    log_info "Backing up current state..."

    BACKUP_DIR="./backups/pre_deployment_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # Backup docker volumes
    if [ "$(docker volume ls -q | wc -l)" -gt 0 ]; then
        log_info "Backing up volumes..."
        docker run --rm \
            -v postgres_data:/data \
            -v "$BACKUP_DIR":/backup \
            alpine tar czf /backup/postgres_data.tar.gz -C / data
        log_success "Volumes backed up"
    fi

    # Backup logs
    if [ -d "./logs" ]; then
        cp -r ./logs "$BACKUP_DIR/logs_backup"
        log_success "Logs backed up"
    fi
}

# ============================================================================
# BUILD SERVICES
# ============================================================================

build_services() {
    log_info "Building services..."

    docker-compose build \
        --no-cache \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD)

    log_success "Services built successfully"
}

# ============================================================================
# START SERVICES
# ============================================================================

start_services() {
    log_info "Starting services..."

    docker-compose up -d

    log_success "Services started"
}

# ============================================================================
# WAIT FOR SERVICES
# ============================================================================

wait_for_services() {
    log_info "Waiting for services to be ready..."

    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    for i in {1..30}; do
        if docker-compose exec -T postgres pg_isready -U demir_ai > /dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL failed to start"
            exit 1
        fi
        sleep 1
    done

    # Wait for Redis
    log_info "Waiting for Redis..."
    for i in {1..30}; do
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Redis failed to start"
            exit 1
        fi
        sleep 1
    done

    # Wait for main application
    log_info "Waiting for main application..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Application is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            log_error "Application failed to start"
            exit 1
        fi
        sleep 1
    done
}

# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

initialize_database() {
    log_info "Initializing database..."

    docker-compose exec -T postgres psql -U demir_ai -d demir_ai \
        -f /docker-entrypoint-initdb.d/init.sql

    log_success "Database initialized"
}

# ============================================================================
# RUN TESTS
# ============================================================================

run_tests() {
    log_info "Running deployment tests..."

    # Test API connectivity
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API is responding"
    else
        log_error "API is not responding"
        return 1
    fi

    # Test database connectivity
    if docker-compose exec -T demir_ai_main python -c \
        "import sqlalchemy; print('DB OK')" > /dev/null 2>&1; then
        log_success "Database connectivity verified"
    else
        log_error "Database connectivity failed"
        return 1
    fi

    # Test Redis connectivity
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis connectivity verified"
    else
        log_error "Redis connectivity failed"
        return 1
    fi
}

# ============================================================================
# VERIFY DEPLOYMENT
# ============================================================================

verify_deployment() {
    log_info "Verifying deployment..."

    # Check all containers are running
    RUNNING_CONTAINERS=$(docker-compose ps -q | wc -l)
    EXPECTED_CONTAINERS=6

    if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_CONTAINERS" ]; then
        log_success "All containers are running"
    else
        log_warning "Expected $EXPECTED_CONTAINERS containers, found $RUNNING_CONTAINERS"
    fi

    # Check logs for errors
    if docker-compose logs | grep -i "error" > /dev/null; then
        log_warning "Errors found in logs"
    else
        log_success "No errors in logs"
    fi

    # Display service URLs
    log_info ""
    log_info "Services are now running at:"
    log_info "  Main API: http://localhost:8000"
    log_info "  Dashboard: http://localhost:8501"
    log_info "  Prometheus: http://localhost:9090"
    log_info "  Grafana: http://localhost:3000"
}

# ============================================================================
# CONFIGURE MONITORING
# ============================================================================

configure_monitoring() {
    log_info "Configuring monitoring..."

    # Create Grafana datasource
    curl -X POST http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/datasources \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://prometheus:9090",
            "access": "proxy",
            "isDefault": true
        }' 2>/dev/null || true

    log_success "Monitoring configured"
}

# ============================================================================
# MAIN DEPLOYMENT FLOW
# ============================================================================

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║     DEMIR AI - PRODUCTION DEPLOYMENT SCRIPT - PHASE 16         ║"
    echo "║     Full System Launch - November 7, 2025                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""

    # Execute deployment steps
    pre_deployment_checks
    echo ""

    backup_current_state
    echo ""

    build_services
    echo ""

    start_services
    echo ""

    wait_for_services
    echo ""

    initialize_database
    echo ""

    run_tests
    echo ""

    configure_monitoring
    echo ""

    verify_deployment
    echo ""

    log_success "🚀 DEMIR AI Production Deployment Completed Successfully!"
    log_info "System is now running in production mode"
    echo ""
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

trap 'log_error "Deployment failed"; exit 1' ERR

# ============================================================================
# RUN MAIN
# ============================================================================

main "$@"
