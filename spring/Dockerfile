FROM eclipse-temurin:17-jdk-jammy AS builder

# 작업 디렉토리를 /app 으로 설정
WORKDIR /app

# 현재 Dockerfile이 있는 폴더(spring)의 모든 파일을 도커 안의 /app 으로 복사
COPY . .

# 실행 권한 부여
RUN chmod +x ./gradlew

# 단일 프로젝트 빌드 (settings.gradle에서 루트가 꼬이는 것 방지)
RUN ./gradlew clean build -x test

# 2단계: 실행 환경 (Runtime)
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# builder 단계에서 생성된 jar 파일 복사 (경로 주의!)
COPY --from=builder /app/build/libs/*-SNAPSHOT.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
