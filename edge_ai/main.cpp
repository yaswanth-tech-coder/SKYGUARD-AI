/**
 * @file main.cpp
 * @brief SkyGuard AI - ESP32 Automatic Weather Station Edge Node Firmware
 * Reads BME280 / SHT31 sensor telemetry, executes real-time AI anomaly detection,
 * prints diagnostic telemetry JSON to Serial / LoRa / MQTT.
 */

#include <Arduino.h>
#include <Wire.h>
#include "skyguard_esp32.h"

// Global SkyGuard Edge AI State
SkyGuardState g_skyguard_state;

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("=================================================");
    Serial.println("  SkyGuard AI - ESP32 Edge Anomaly Sentinel v1.0 ");
    Serial.println("  Core Triad: Temp (°C), Press (hPa), RH (%)     ");
    Serial.println("=================================================");

    // Initialize SkyGuard AI engine state
    skyguard_init(&g_skyguard_state);
    Serial.println("[INFO] SkyGuard AI Edge Engine Initialized (<6 KB RAM allocated).");
}

void loop() {
    // 1. Simulate reading from physical digital sensor (e.g. BME280 / SHT31)
    SkyGuardReading reading;
    
    // Base diurnal fluctuation
    static float sim_time_hours = 12.0f;
    sim_time_hours += 0.25f;
    if (sim_time_hours >= 24.0f) sim_time_hours = 0.0f;

    reading.temperature_c = 28.0f + 6.0f * sinf((sim_time_hours - 8.0f) * 0.2618f);
    reading.humidity_pct = 60.0f - 18.0f * sinf((sim_time_hours - 8.0f) * 0.2618f);
    reading.pressure_hpa = 1012.5f + 1.2f * cosf(sim_time_hours * 0.5236f);

    // Occasional simulated sensor fault for demonstration
    static int cycle = 0;
    cycle++;
    if (cycle == 10) {
        Serial.println("\n[SIMULATION] Injecting +18°C Electrical Transient Spike...");
        reading.temperature_c += 18.0f;
    } else if (cycle == 20) {
        Serial.println("\n[SIMULATION] Injecting Super-Saturation Thermodynamic Violation (RH=100% @ 35°C)...");
        reading.humidity_pct = 100.0f;
        reading.temperature_c = 35.0f;
    }

    // 2. Measure Execution Latency on ESP32
    uint32_t t_start = micros();
    SkyGuardResult result = skyguard_process_reading(&g_skyguard_state, &reading);
    uint32_t latency_us = micros() - t_start;

    // 3. Output Telemetry & Diagnostics
    Serial.printf(
        "{\"timestamp_h\": %.2f, \"temp_c\": %.2f, \"rh_pct\": %.2f, \"press_hpa\": %.2f, "
        "\"dew_point_c\": %.2f, \"is_anomaly\": %s, \"score\": %.3f, \"health_pct\": %.1f, "
        "\"root_cause\": \"%s\", \"action\": \"%s\", \"latency_us\": %u}\n",
        sim_time_hours,
        reading.temperature_c,
        reading.humidity_pct,
        reading.pressure_hpa,
        reading.dew_point_c,
        result.is_anomaly ? "true" : "false",
        result.composite_anomaly_score,
        result.sensor_health_index,
        result.root_cause,
        result.maintenance_action,
        latency_us
    );

    delay(2000); // 2-second telemetry interval
}
