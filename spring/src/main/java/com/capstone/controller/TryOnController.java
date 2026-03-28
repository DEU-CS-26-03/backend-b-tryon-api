package com.capstone.controller;

import java.io.IOException;

import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.capstone.service.TryOnService;

@RestController
@RequestMapping("/api/fitting")
public class TryOnController {

    private final TryOnService tryOnService;

    public TryOnController(TryOnService tryOnService) {
        this.tryOnService = tryOnService;
    }

    @PostMapping(
            value = "/tryon",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<byte[]> tryOn(
            @RequestPart("person") MultipartFile person,
            @RequestPart("garment") MultipartFile garment
    ) throws IOException {

        ResponseEntity<byte[]> response = tryOnService.requestTryOn(person, garment);

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=tryon-result.jpg")
                .contentType(MediaType.IMAGE_JPEG)
                .body(response.getBody());
    }
}
