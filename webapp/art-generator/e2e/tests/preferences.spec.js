const { test, expect } = require('@playwright/test');

test.describe('Preference Learning', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Navigate to Compare & Learn tab
    await page.click('text=Compare & Learn');
  });

  test('should display preference learning sections', async ({ page }) => {
    await expect(page.locator('text=A/B Comparison')).toBeVisible();
    await expect(page.locator('text=Rate Images')).toBeVisible();
    await expect(page.locator('text=Rank Your Favorites')).toBeVisible();
  });

  test('should start A/B comparison', async ({ page }) => {
    // Click start comparison button
    await page.click('button:has-text("Start Comparison")');
    
    // Should display two images for comparison
    const comparisonImages = page.locator('text=A/B Comparison').locator('..').locator('img');
    await expect(comparisonImages).toHaveCount(2);
  });

  test('should submit comparison preference', async ({ page }) => {
    // Start comparison
    await page.click('button:has-text("Start Comparison")');
    
    // Click on the first image to select it as preferred
    const firstImage = page.locator('text=A/B Comparison').locator('..').locator('img').first();
    await firstImage.click();
    
    // Should show success message
    await expect(page.locator('text=Preference recorded!')).toBeVisible();
  });

  test('should allow rating individual images', async ({ page }) => {
    // Click on an image in the rating section
    const ratingImages = page.locator('text=Rate Images').locator('..').locator('img');
    
    if (await ratingImages.count() > 0) {
      await ratingImages.first().click();
      
      // Should show rating slider
      await expect(page.locator('text=Rating:')).toBeVisible();
      
      // Adjust slider
      const slider = page.locator('[role="slider"]');
      await slider.click();
      
      // Submit rating
      await page.click('button:has-text("Submit Rating")');
      
      // Should show success message
      await expect(page.locator('text=Rating submitted!')).toBeVisible();
    }
  });

  test('should display ranking interface', async ({ page }) => {
    // Should show draggable ranking items
    const rankingSection = page.locator('text=Rank Your Favorites').locator('..');
    
    // Check for ranking numbers
    await expect(rankingSection.locator('text=#1')).toBeVisible();
    
    // Check for drag handles
    const dragHandles = rankingSection.locator('[data-testid="DragHandleIcon"]');
    const handleCount = await dragHandles.count();
    
    expect(handleCount).toBeGreaterThan(0);
  });

  test('should navigate to gallery and show predictions', async ({ page }) => {
    // Navigate to Gallery tab
    await page.click('text=Gallery');
    
    // Should show gallery interface
    await expect(page.locator('input[placeholder*="Search prompts"]')).toBeVisible();
    
    // Should have sort options
    await expect(page.locator('text=Sort By')).toBeVisible();
    
    // Select predicted preference sort
    await page.click('text=Sort By');
    await page.click('text=Predicted Preference');
    
    // Should show loading predictions message
    await expect(page.locator('text=Loading preference predictions')).toBeVisible();
  });
});