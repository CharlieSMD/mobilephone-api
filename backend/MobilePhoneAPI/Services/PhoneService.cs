using Microsoft.EntityFrameworkCore;
using MobilePhoneAPI.Data;
using MobilePhoneAPI.Models;

namespace MobilePhoneAPI.Services;

public interface IPhoneService
{
    Task<List<Phone>> GetAllPhonesAsync();
    Task<Phone?> GetPhoneByIdAsync(int id);
    Task<List<Phone>> SearchPhonesAsync(string searchTerm);
    Task<List<Phone>> GetPhonesByBrandAsync(string brand);
}

public class PhoneService : IPhoneService
{
    private readonly ApplicationDbContext _context;

    public PhoneService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<List<Phone>> GetAllPhonesAsync()
    {
        return await _context.Phones
            .OrderBy(p => p.Brand)
            .ThenBy(p => p.Model)
            .ToListAsync();
    }

    public async Task<Phone?> GetPhoneByIdAsync(int id)
    {
        return await _context.Phones
            .FirstOrDefaultAsync(p => p.Id == id);
    }

    public async Task<List<Phone>> SearchPhonesAsync(string searchTerm)
    {
        if (string.IsNullOrWhiteSpace(searchTerm))
            return await GetAllPhonesAsync();

        searchTerm = searchTerm.ToLower();
        return await _context.Phones
            .Where(p => 
                p.Brand.ToLower().Contains(searchTerm) ||
                p.Model.ToLower().Contains(searchTerm) ||
                p.Storage.ToLower().Contains(searchTerm)
            )
            .OrderBy(p => p.Brand)
            .ThenBy(p => p.Model)
            .ToListAsync();
    }

    public async Task<List<Phone>> GetPhonesByBrandAsync(string brand)
    {
        if (string.IsNullOrWhiteSpace(brand))
            return await GetAllPhonesAsync();

        return await _context.Phones
            .Where(p => p.Brand.Equals(brand, StringComparison.OrdinalIgnoreCase))
            .OrderBy(p => p.Model)
            .ToListAsync();
    }
} 