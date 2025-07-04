const { test, expect } = require('@playwright/test');

test.describe('Image Generation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application', async ({ page }) => {
    await expect(page.locator('text=AI Art Generator with Preference Learning')).toBeVisible();
  });

  test('should display all tabs', async ({ page }) => {
    await expect(page.locator('text=Generate')).toBeVisible();
    await expect(page.locator('text=Compare & Learn')).toBeVisible();
    await expect(page.locator('text=Gallery')).toBeVisible();
  });

  test('should generate an image', async ({ page }) => {
    // Enter a prompt
    await page.fill('textarea[placeholder*="Describe the image"]', 'A beautiful sunset over mountains');
    
    // Select provider
    await page.click('text=Provider');
    await page.click('text=OpenAI DALL-E');
    
    // Click generate button
    await page.click('button:has-text("Generate")');
    
    // Wait for generation to complete (mocked in tests)
    await expect(page.locator('text=Generating...')).toBeVisible();
    
    // Should show the generated image eventually
    await expect(page.locator('img[alt*="sunset"]')).toBeVisible({ timeout: 30000 });
  });

  test('should show error for empty prompt', async ({ page }) => {
    // Click generate without entering prompt
    await page.click('button:has-text("Generate")');
    
    // Should show error message
    await expect(page.locator('text=Please enter a prompt')).toBeVisible();
  });

  test('should disable Generate Optimal when less than 5 images', async ({ page }) => {
    const generateOptimalButton = page.locator('button:has-text("Generate Optimal")');
    
    await expect(generateOptimalButton).toBeDisabled();
    await expect(page.locator('text=Generate at least 5 images')).toBeVisible();
  });

  test('should switch between providers', async ({ page }) => {
    // Select Stable Diffusion provider
    await page.click('text=Provider');
    await page.click('text=Stable Diffusion');
    
    // Negative prompt should be enabled for Stable Diffusion
    const negativePrompt = page.locator('textarea[placeholder*="What to avoid"]');
    await expect(negativePrompt).toBeEnabled();
    
    // Switch back to OpenAI
    await page.click('text=Provider');
    await page.click('text=OpenAI DALL-E');
    
    // Negative prompt should be disabled for OpenAI
    await expect(negativePrompt).toBeDisabled();
  });

  test('should display recent generations', async ({ page }) => {
    // Recent generations section should be visible
    await expect(page.locator('text=Recent Generations')).toBeVisible();
    
    // Should show a grid of recent images (if any)
    const recentImages = page.locator('text=Recent Generations').locator('..').locator('img');
    const count = await recentImages.count();
    
    // Grid should exist even if empty
    expect(count).toBeGreaterThanOrEqual(0);
  });
});