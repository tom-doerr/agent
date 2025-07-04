import { test, expect } from '@playwright/test';

test.describe('Audio Recording Feature', () => {
  test.beforeEach(async ({ page, context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);
    await page.goto('http://localhost:3000');
  });

  test('should display audio recorder button', async ({ page }) => {
    const recordButton = page.getByTestId('record-button');
    await expect(recordButton).toBeVisible();
    await expect(recordButton).toHaveText('🎤 Start Recording');
  });

  test('should start recording when button clicked', async ({ page }) => {
    const recordButton = page.getByTestId('record-button');
    
    // Click to start recording
    await recordButton.click();
    
    // Button should change to stop recording
    await expect(recordButton).toHaveText('🛑 Stop Recording');
    await expect(recordButton).toHaveClass(/recording/);
  });

  test('should stop recording and show audio preview', async ({ page }) => {
    const recordButton = page.getByTestId('record-button');
    
    // Start recording
    await recordButton.click();
    await expect(recordButton).toHaveText('🛑 Stop Recording');
    
    // Wait a bit to simulate recording
    await page.waitForTimeout(1000);
    
    // Stop recording
    await recordButton.click();
    await expect(recordButton).toHaveText('🎤 Start Recording');
    
    // Audio preview should appear
    const audioElement = page.locator('audio');
    await expect(audioElement).toBeVisible();
  });

  test('should transcribe audio and populate question field', async ({ page }) => {
    // Mock the transcription endpoint
    await page.route('**/transcribe', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          text: 'What is the weather today?',
          status: 'success'
        })
      });
    });

    const recordButton = page.getByTestId('record-button');
    const questionInput = page.getByTestId('question-input');
    
    // Start recording
    await recordButton.click();
    await page.waitForTimeout(500);
    
    // Stop recording
    await recordButton.click();
    
    // Wait for transcription to complete
    await expect(questionInput).toHaveValue('What is the weather today?');
  });

  test('should handle transcription errors gracefully', async ({ page }) => {
    // Mock transcription error
    await page.route('**/transcribe', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Transcription service unavailable'
        })
      });
    });

    const recordButton = page.getByTestId('record-button');
    
    // Set up console listener to catch error logs
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Start and stop recording
    await recordButton.click();
    await page.waitForTimeout(500);
    await recordButton.click();
    
    // Should log transcription error
    await page.waitForTimeout(1000);
    expect(consoleErrors.some(err => err.includes('Transcription error'))).toBeTruthy();
  });

  test('should integrate with main question flow', async ({ page }) => {
    // Mock both transcription and streaming endpoints
    await page.route('**/transcribe', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          text: 'What is FastAPI?',
          status: 'success'
        })
      });
    });

    await page.route('**/stream/*', async (route) => {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode('data: {"start": true}\n\n'));
          controller.enqueue(encoder.encode('data: {"chunk": "FastAPI is "}\n\n'));
          controller.enqueue(encoder.encode('data: {"chunk": "a modern web framework"}\n\n'));
          controller.enqueue(encoder.encode('data: {"done": true}\n\n'));
          controller.close();
        }
      });
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: stream
      });
    });

    const recordButton = page.getByTestId('record-button');
    const submitButton = page.getByTestId('submit-button');
    
    // Record audio
    await recordButton.click();
    await page.waitForTimeout(500);
    await recordButton.click();
    
    // Wait for transcription
    await expect(page.getByTestId('question-input')).toHaveValue('What is FastAPI?');
    
    // Submit question
    await submitButton.click();
    
    // Check response appears
    await expect(page.getByTestId('response')).toContainText('FastAPI is a modern web framework');
  });

  test('should handle microphone permission denial', async ({ page, context }) => {
    // Create new context without microphone permission
    const deniedContext = await page.context().browser().newContext({
      permissions: []
    });
    const deniedPage = await deniedContext.newPage();
    
    await deniedPage.goto('http://localhost:3000');
    
    // Mock getUserMedia to throw permission error
    await deniedPage.addInitScript(() => {
      navigator.mediaDevices.getUserMedia = async () => {
        throw new Error('Permission denied');
      };
    });
    
    const recordButton = deniedPage.getByTestId('record-button');
    
    // Set up dialog handler
    deniedPage.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Could not access microphone');
      await dialog.accept();
    });
    
    // Try to start recording
    await recordButton.click();
    
    // Button should remain in initial state
    await expect(recordButton).toHaveText('🎤 Start Recording');
    
    await deniedContext.close();
  });
});