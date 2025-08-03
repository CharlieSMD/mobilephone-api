using System.Text.Json;
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
    private readonly string _dataFilePath;
    private List<Phone>? _phones;

    public PhoneService(IWebHostEnvironment environment)
    {
        // Get JSON file path
        _dataFilePath = Path.Combine(environment.ContentRootPath, "..", "..", "phones_data.json");
    }

    private async Task<List<Phone>> LoadPhonesAsync()
    {
        if (_phones != null)
            return _phones;

        try
        {
            if (!File.Exists(_dataFilePath))
            {
                throw new FileNotFoundException($"Phone data file not found: {_dataFilePath}");
            }

            var jsonContent = await File.ReadAllTextAsync(_dataFilePath);
            _phones = JsonSerializer.Deserialize<List<Phone>>(jsonContent, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            }) ?? new List<Phone>();

            return _phones;
        }
        catch (Exception ex)
        {
            // Return empty list if reading fails
            return new List<Phone>();
        }
    }

    public async Task<List<Phone>> GetAllPhonesAsync()
    {
        return await LoadPhonesAsync();
    }

    public async Task<Phone?> GetPhoneByIdAsync(int id)
    {
        var phones = await LoadPhonesAsync();
        return phones.FirstOrDefault(p => p.Id == id);
    }

    public async Task<List<Phone>> SearchPhonesAsync(string searchTerm)
    {
        var phones = await LoadPhonesAsync();
        if (string.IsNullOrWhiteSpace(searchTerm))
            return phones;

        searchTerm = searchTerm.ToLower();
        return phones.Where(p => 
            p.Brand.ToLower().Contains(searchTerm) ||
            p.Model.ToLower().Contains(searchTerm) ||
            p.Storage.ToLower().Contains(searchTerm)
        ).ToList();
    }

    public async Task<List<Phone>> GetPhonesByBrandAsync(string brand)
    {
        var phones = await LoadPhonesAsync();
        if (string.IsNullOrWhiteSpace(brand))
            return phones;

        return phones.Where(p => 
            p.Brand.Equals(brand, StringComparison.OrdinalIgnoreCase)
        ).ToList();
    }
} 