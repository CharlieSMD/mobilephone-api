using Microsoft.EntityFrameworkCore;
using MobilePhoneAPI.Data;
using MobilePhoneAPI.Models;

namespace MobilePhoneAPI.Services;

public class FavoriteService : IFavoriteService
{
    private readonly ApplicationDbContext _context;

    public FavoriteService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<bool> AddFavoriteAsync(int userId, int phoneId)
    {
        // Check if already favorited
        var existingFavorite = await _context.Favorites
            .FirstOrDefaultAsync(f => f.UserId == userId && f.PhoneId == phoneId);

        if (existingFavorite != null)
        {
            return false; // Already favorited
        }

        // Check if phone exists
        var phoneExists = await _context.Phones.AnyAsync(p => p.Id == phoneId);
        if (!phoneExists)
        {
            throw new InvalidOperationException("Phone not found");
        }

        // Add favorite
        var favorite = new Favorite
        {
            UserId = userId,
            PhoneId = phoneId,
            CreatedAt = DateTime.UtcNow
        };

        _context.Favorites.Add(favorite);
        await _context.SaveChangesAsync();

        return true;
    }

    public async Task<bool> RemoveFavoriteAsync(int userId, int phoneId)
    {
        var favorite = await _context.Favorites
            .FirstOrDefaultAsync(f => f.UserId == userId && f.PhoneId == phoneId);

        if (favorite == null)
        {
            return false; // Not favorited
        }

        _context.Favorites.Remove(favorite);
        await _context.SaveChangesAsync();

        return true;
    }

    public async Task<bool> IsFavoriteAsync(int userId, int phoneId)
    {
        return await _context.Favorites
            .AnyAsync(f => f.UserId == userId && f.PhoneId == phoneId);
    }

    public async Task<List<Phone>> GetUserFavoritesAsync(int userId)
    {
        return await _context.Favorites
            .Where(f => f.UserId == userId)
            .Include(f => f.Phone)
            .Select(f => f.Phone)
            .ToListAsync();
    }

    public async Task<List<int>> GetUserFavoriteIdsAsync(int userId)
    {
        return await _context.Favorites
            .Where(f => f.UserId == userId)
            .Select(f => f.PhoneId)
            .ToListAsync();
    }
}
