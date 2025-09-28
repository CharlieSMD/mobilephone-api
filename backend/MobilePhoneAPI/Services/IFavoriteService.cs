using MobilePhoneAPI.Models;

namespace MobilePhoneAPI.Services;

public interface IFavoriteService
{
    Task<bool> AddFavoriteAsync(int userId, int phoneId);
    Task<bool> RemoveFavoriteAsync(int userId, int phoneId);
    Task<bool> IsFavoriteAsync(int userId, int phoneId);
    Task<List<Phone>> GetUserFavoritesAsync(int userId);
    Task<List<int>> GetUserFavoriteIdsAsync(int userId);
}
