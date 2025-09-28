using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using MobilePhoneAPI.Services;

namespace MobilePhoneAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize] // Require authentication for all favorite operations
public class FavoriteController : ControllerBase
{
    private readonly IFavoriteService _favoriteService;

    public FavoriteController(IFavoriteService favoriteService)
    {
        _favoriteService = favoriteService;
    }

    [HttpPost("{phoneId}")]
    public async Task<IActionResult> AddFavorite(int phoneId)
    {
        try
        {
            var userId = GetCurrentUserId();
            var result = await _favoriteService.AddFavoriteAsync(userId, phoneId);

            if (result)
            {
                return Ok(new { message = "Phone added to favorites successfully" });
            }
            else
            {
                return BadRequest(new { message = "Phone is already in favorites" });
            }
        }
        catch (InvalidOperationException ex)
        {
            return NotFound(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "An error occurred while adding to favorites" });
        }
    }

    [HttpDelete("{phoneId}")]
    public async Task<IActionResult> RemoveFavorite(int phoneId)
    {
        try
        {
            var userId = GetCurrentUserId();
            var result = await _favoriteService.RemoveFavoriteAsync(userId, phoneId);

            if (result)
            {
                return Ok(new { message = "Phone removed from favorites successfully" });
            }
            else
            {
                return BadRequest(new { message = "Phone is not in favorites" });
            }
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "An error occurred while removing from favorites" });
        }
    }

    [HttpGet("{phoneId}/status")]
    public async Task<IActionResult> GetFavoriteStatus(int phoneId)
    {
        try
        {
            var userId = GetCurrentUserId();
            var isFavorite = await _favoriteService.IsFavoriteAsync(userId, phoneId);

            return Ok(new { isFavorite });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "An error occurred while checking favorite status" });
        }
    }

    [HttpGet("user")]
    public async Task<IActionResult> GetUserFavorites()
    {
        try
        {
            var userId = GetCurrentUserId();
            var favorites = await _favoriteService.GetUserFavoritesAsync(userId);

            return Ok(favorites);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "An error occurred while retrieving favorites" });
        }
    }

    [HttpGet("user/ids")]
    public async Task<IActionResult> GetUserFavoriteIds()
    {
        try
        {
            var userId = GetCurrentUserId();
            var favoriteIds = await _favoriteService.GetUserFavoriteIdsAsync(userId);

            return Ok(favoriteIds);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "An error occurred while retrieving favorite IDs" });
        }
    }

    private int GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrEmpty(userIdClaim) || !int.TryParse(userIdClaim, out int userId))
        {
            throw new UnauthorizedAccessException("Invalid user ID");
        }
        return userId;
    }
}
