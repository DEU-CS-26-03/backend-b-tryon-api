package com.capstone.service;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class TryOnService {

    private final RestTemplate restTemplate;

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    public TryOnService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public ResponseEntity<byte[]> requestTryOn(MultipartFile person, MultipartFile garment) throws IOException {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();

        //ByteArrayResource에서 getFilename()을 오버라이드하지 않으면 파일명이 빠져서 상대 서버가 multipart 처리에 실패할 수 있다.
        ByteArrayResource personResource = new ByteArrayResource(person.getBytes()) {
            @Override
            public String getFilename() {
                return person.getOriginalFilename();
            }
        };

        ByteArrayResource garmentResource = new ByteArrayResource(garment.getBytes()) {
            @Override
            public String getFilename() {
                return garment.getOriginalFilename();
            }
        };

        HttpHeaders personPartHeaders = new HttpHeaders();
        personPartHeaders.setContentDisposition(
                ContentDisposition.builder("form-data")
                        .name("person")
                        .filename(person.getOriginalFilename())
                        .build()
        );
        personPartHeaders.setContentType(MediaType.parseMediaType(
                person.getContentType() != null ? person.getContentType() : "image/jpeg"
        ));

        HttpHeaders garmentPartHeaders = new HttpHeaders();
        garmentPartHeaders.setContentDisposition(
                ContentDisposition.builder("form-data")
                        .name("garment")
                        .filename(garment.getOriginalFilename())
                        .build()
        );
        garmentPartHeaders.setContentType(MediaType.parseMediaType(
                garment.getContentType() != null ? garment.getContentType() : "image/jpeg"
        ));

        body.add("person", new HttpEntity<>(personResource, personPartHeaders));
        body.add("garment", new HttpEntity<>(garmentResource, garmentPartHeaders));

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        ResponseEntity<byte[]> response = restTemplate.postForEntity(
                pythonServiceUrl + "/tryon",
                requestEntity,
                byte[].class
        );

        return ResponseEntity
                .status(response.getStatusCode())
                .contentType(MediaType.IMAGE_JPEG)
                .body(response.getBody());
    }
}
