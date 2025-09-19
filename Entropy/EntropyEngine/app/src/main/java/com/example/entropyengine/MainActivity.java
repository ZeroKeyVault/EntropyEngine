package com.example.entropyengine;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends AppCompatActivity {

    private Button btnBaseSearch, btnAdvancedSearch;
    private TextView tvResults, tvStatus;
    private ProgressBar progressBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Python
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        // Initialize UI components
        btnBaseSearch = findViewById(R.id.btnBaseSearch);
        btnAdvancedSearch = findViewById(R.id.btnAdvancedSearch);
        tvResults = findViewById(R.id.tvResults);
        tvStatus = findViewById(R.id.tvStatus);
        progressBar = findViewById(R.id.progressBar);

        // Set up button click listeners
        btnBaseSearch.setOnClickListener(v -> runScraper("base"));
        btnAdvancedSearch.setOnClickListener(v -> runScraper("advanced"));
    }

    private void runScraper(String type) {
        // Show loading state
        progressBar.setVisibility(View.VISIBLE);
        tvStatus.setText("Loading...");
        btnBaseSearch.setEnabled(false);
        btnAdvancedSearch.setEnabled(false);
        tvResults.setText("");

        // Run in background thread to avoid blocking UI
        new Thread(() -> {
            try {
                Python py = Python.getInstance();
                String result;
                
                if (type.equals("base")) {
                    result = py.getModule("scraper").callAttr("base_search").toString();
                } else {
                    result = py.getModule("scraper").callAttr("advanced_engine_search").toString();
                }
                
                // Update UI on main thread
                runOnUiThread(() -> {
                    tvResults.setText(result);
                    tvStatus.setText("Completed");
                    progressBar.setVisibility(View.GONE);
                    btnBaseSearch.setEnabled(true);
                    btnAdvancedSearch.setEnabled(true);
                });
            } catch (Exception e) {
                // Handle errors
                runOnUiThread(() -> {
                    tvResults.setText("Error: " + e.getMessage());
                    tvStatus.setText("Failed");
                    progressBar.setVisibility(View.GONE);
                    btnBaseSearch.setEnabled(true);
                    btnAdvancedSearch.setEnabled(true);
                });
            }
        }).start();
    }
}