#!/bin/sh

# Kubernetes 배포 스크립트
set -e

# 환경 변수 설정
BUILD_NUMBER=${1:-"latest"}
GIT_BRANCH=${2:-"main"}
NAMESPACE=${3:-"default"}
ACTION=${4:-"deploy"}

echo "🔍 실행 정보:"
echo "BUILD_NUMBER: ${BUILD_NUMBER}"
echo "GIT_BRANCH: ${GIT_BRANCH}"
echo "NAMESPACE: ${NAMESPACE}"
echo "ACTION: ${ACTION}"

# 프론트엔드 빌드 함수
build_frontend() {
    echo "🚀 프론트엔드 빌드 시작..."
    
    # 도메인 생성 (기존 로직 재사용)
    clean_branch=$(echo "${GIT_BRANCH}" | sed 's|^origin/||')
    echo "🔍 정리된 브랜치: ${clean_branch}"
    
    domain_suffix=""
    if [ "${clean_branch}" = "main" ]; then
        domain_suffix=""
    elif [ "${clean_branch}" = "qa" ]; then
        domain_suffix="-qa"
    else
        domain_suffix="-${clean_branch}"
    fi
    
    domain="drillquiz${domain_suffix}.new-nation.church"
    echo "✅ 생성된 도메인: ${domain}"
    
    # 환경 변수 파일 치환
    echo "🔧 환경 변수 파일 치환 중..."
    sed -i "s/DOMAIN_PLACEHOLDER/${domain}/g" env-frontend
    sed -i "s/DOMAIN_PLACEHOLDER/${domain}/g" env
    sed -i "s/DOMAIN_PLACEHOLDER/${domain}/g" package.json
    echo "✅ 환경 변수 파일 치환 완료"
    
    # 프론트엔드 Docker 이미지 빌드
    echo "🔨 프론트엔드 Docker 이미지 빌드 중..."
    image_frontend="doohee323/drillquiz-frontend:${BUILD_NUMBER}"
    cp -Rf Dockerfile.frontend Dockerfile
    docker build -t ${image_frontend} .
    
    # 컨테이너에서 빌드 파일 추출
    echo "📦 컨테이너에서 빌드 파일 추출 중..."
    docker create --name frontend-extract ${image_frontend}
    docker cp frontend-extract:/usr/share/nginx/html ./frontend-dist
    docker rm frontend-extract
    
    # public 디렉토리로 파일 복사
    echo "📁 public 디렉토리로 파일 복사 중..."
    rm -rf public/*
    cp -Rf frontend-dist/* public/
    rm -rf frontend-dist
    
    echo "✅ 프론트엔드 빌드 완료!"
}

# 배포 함수
deploy_to_kubernetes() {
    echo "🔍 배포 정보:"
    echo "BUILD_NUMBER: ${BUILD_NUMBER}"
    echo "GIT_BRANCH: ${GIT_BRANCH}"
    echo "NAMESPACE: ${NAMESPACE}"
    
    # kubectl 다운로드 (배포 시에만)
    echo "📥 kubectl 다운로드 중..."
    wget https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && chmod +x ./kubectl

    # Git 정보 확인
    echo "--- Git 정보 ---"
    git rev-parse --abbrev-ref HEAD || echo "git rev-parse 명령어 실패"



# BUILD_NUMBER가 null이면 latest로 설정
if [ -z "${BUILD_NUMBER}" ] || [ "${BUILD_NUMBER}" = "null" ]; then
    BUILD_NUMBER="latest"
fi

# GIT_BRANCH가 null이면 Git 명령어로 확인
if [ -z "${GIT_BRANCH}" ] || [ "${GIT_BRANCH}" = "null" ]; then
    echo "GIT_BRANCH가 null이므로 Git 명령어로 확인합니다"
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    echo "Git 명령어로 확인된 브랜치: ${GIT_BRANCH}"
fi

# origin/ 접두사 제거
GIT_BRANCH=$(echo "${GIT_BRANCH}" | sed 's|^origin/||')
echo "🔍 정리된 GIT_BRANCH: ${GIT_BRANCH}"

# 브랜치에 따른 STAGING과 도메인 설정
if [ "${GIT_BRANCH}" = "main" ]; then
    STAGING="prod"
    DOMAIN_SUFFIX=""
elif [ "${GIT_BRANCH}" = "qa" ]; then
    STAGING="qa"
    DOMAIN_SUFFIX="-qa"
else
    STAGING="dev"
    DOMAIN_SUFFIX="-${GIT_BRANCH}"
fi

# 도메인 생성 (통합 배포)
DOMAIN="drillquiz${DOMAIN_SUFFIX}.new-nation.church"

echo "✅ STAGING: ${STAGING}"
echo "✅ 생성된 도메인: ${DOMAIN}"

if [ "${STAGING}" = "qa" ]; then
    cp -Rf ci/k8s-qa.yaml ci/k8s.yaml
elif [ "${STAGING}" = "prod" ]; then
    echo ""
else
    cp -Rf ci/k8s-dev.yaml ci/k8s.yaml
fi

# Secret 이름 처리 (정규화된 GIT_BRANCH 사용)
SECRET_SUFFIX="${GIT_BRANCH}"
if [ "${SECRET_SUFFIX}" = "null" ]; then
    SECRET_SUFFIX="main"
fi
# / 문자를 - 로 변경
SECRET_SUFFIX=$(echo "${SECRET_SUFFIX}" | sed 's|/|-|g')
echo "Secret 이름에 사용할 SUFFIX: ${SECRET_SUFFIX}"

# 환경 변수 파일 치환 (먼저 수행)
echo "🔧 환경 변수 파일 치환 중..."
echo "🔍 치환할 도메인: ${DOMAIN}"
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" env-frontend
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" env
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" package.json
echo "✅ 환경 변수 파일 치환 완료"

# k8s.yaml 파일 치환
echo "🔧 k8s.yaml 파일 치환 중..."
echo "치환할 값들:"
echo "  BUILD_NUMBER: ${BUILD_NUMBER}"
echo "  GIT_BRANCH: ${SECRET_SUFFIX}"
echo "  STAGING: ${STAGING}"
echo "  DOMAIN: ${DOMAIN}"

# DOMAIN_PLACEHOLDER 치환
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" ci/k8s.yaml
sed -i "s/BUILD_NUMBER_PLACEHOLDER/${BUILD_NUMBER}/g" ci/k8s.yaml
sed -i "s/STAGING/${STAGING}/g" ci/k8s.yaml
sed -i "s/GIT_BRANCH/${SECRET_SUFFIX}/g" ci/k8s.yaml

# Secret 생성 (치환된 env 파일 사용)
echo "🔐 Secret 생성 중..."
kubectl -n ${NAMESPACE} create secret generic drillquiz-env-secret-${SECRET_SUFFIX} --from-env-file=env --dry-run=client -o yaml | kubectl -n ${NAMESPACE} apply -f -



# 기존 리소스 삭제 (실패해도 계속 진행)
echo "🗑️  기존 리소스 삭제 중..."
kubectl -n ${NAMESPACE} delete -f ci/k8s.yaml || echo "삭제할 리소스가 없습니다 (정상)"

# 새 리소스 배포
echo "🚀 새 리소스 배포 중..."
kubectl -n ${NAMESPACE} apply -f ci/k8s.yaml

echo "✅ 배포 완료!"
}

# 메인 실행 로직
case "${ACTION}" in
    "build-frontend")
        build_frontend
        ;;
    "deploy")
        deploy_to_kubernetes
        ;;
    *)
        echo "❌ 잘못된 ACTION: ${ACTION}"
        echo "사용법: $0 <BUILD_NUMBER> <GIT_BRANCH> <NAMESPACE> [build-frontend|deploy]"
        exit 1
        ;;
esac

