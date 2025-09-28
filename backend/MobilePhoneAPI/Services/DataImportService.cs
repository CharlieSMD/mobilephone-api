using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.Configuration.Attributes;
using Microsoft.EntityFrameworkCore;
using MobilePhoneAPI.Data;
using MobilePhoneAPI.Models;
using System.Globalization;
using System.Text;

namespace MobilePhoneAPI.Services;

public interface IDataImportService
{
    Task<int> ImportPhonesFromCsvAsync(string csvFilePath);
}

public class DataImportService : IDataImportService
{
    private readonly ApplicationDbContext _context;

    public DataImportService(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<int> ImportPhonesFromCsvAsync(string csvFilePath)
    {
        if (!File.Exists(csvFilePath))
        {
            throw new FileNotFoundException($"CSV file not found: {csvFilePath}");
        }

        var importedCount = 0;
        
        using var reader = new StreamReader(csvFilePath, Encoding.UTF8);
        using var csv = new CsvReader(reader, new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HeaderValidated = null,
            MissingFieldFound = null,
            HasHeaderRecord = true,
            Delimiter = ",",
            TrimOptions = TrimOptions.Trim
        });

        var records = csv.GetRecords<CsvPhoneRecord>();

        // Debug: Check first few records
        var recordList = records.ToList();
        Console.WriteLine($"Total records found: {recordList.Count}");
        
        for (int i = 0; i < Math.Min(5, recordList.Count); i++)
        {
            var record = recordList[i];
            Console.WriteLine($"Record {i}: Brand='{record.Brand}', Model='{record.Model}'");
        }

        foreach (var record in recordList)
        {
            // Debug logging
            Console.WriteLine($"Processing: {record.Brand} {record.Model}");
            
            // Skip if phone already exists
            var existingPhone = await _context.Phones
                .FirstOrDefaultAsync(p => p.Brand == record.Brand && p.Model == record.Model);

            if (existingPhone != null)
            {
                continue;
            }

            // Create new phone record
            var phone = new Phone
            {
                Brand = record.Brand?.Trim() ?? "",
                Model = record.Model?.Trim() ?? "",
                Storage = record.Storage?.Trim() ?? "",
                Ram = record.Ram?.Trim() ?? "",
                ScreenSize = record.ScreenSize?.Trim() ?? "",
                Camera = record.Camera?.Trim() ?? "",
                Battery = record.Battery?.Trim() ?? "",
                ImageUrl = record.ImageUrl?.Trim() ?? GeneratePlaceholderImageUrl(record.Brand, record.Model),
                // Detailed specifications
                Weight = record.Weight,
                Dimensions = record.Dimensions?.Trim(),
                Processor = record.Processor?.Trim(),
                Os = record.Os?.Trim(),
                ReleaseYear = record.ReleaseYear,
                NetworkType = record.NetworkType?.Trim(),
                ChargingPower = record.ChargingPower?.Trim(),
                WaterResistance = record.WaterResistance?.Trim(),
                Material = record.Material?.Trim(),
                Colors = record.Colors?.Trim(),
                ColorImages = record.ColorImages?.Trim(),
                ImageFront = record.ImageFront?.Trim(),
                ImageBack = record.ImageBack?.Trim(),
                ImageSide = record.ImageSide?.Trim()
            };

            _context.Phones.Add(phone);
            importedCount++;
        }

        await _context.SaveChangesAsync();
        return importedCount;
    }

    private string GeneratePlaceholderImageUrl(string? brand, string? model)
    {
        var text = $"{brand} {model}";
        var encodedText = Uri.EscapeDataString(text);
        return $"https://via.placeholder.com/400x600/4A90E2/FFFFFF?text={encodedText}";
    }
}

// CSV record model
public class CsvPhoneRecord
{
    [Name("Brand")]
    public string? Brand { get; set; }
    
    [Name("Model")]
    public string? Model { get; set; }
    
    [Name("Storage")]
    public string? Storage { get; set; }
    
    [Name("Ram")]
    public string? Ram { get; set; }
    
    [Name("ScreenSize")]
    public string? ScreenSize { get; set; }
    
    [Name("Camera")]
    public string? Camera { get; set; }
    
    [Name("Battery")]
    public string? Battery { get; set; }
    
    // Detailed specifications
    [Name("Weight")]
    public decimal? Weight { get; set; }
    
    [Name("Dimensions")]
    public string? Dimensions { get; set; }
    
    [Name("Processor")]
    public string? Processor { get; set; }
    
    [Name("Os")]
    public string? Os { get; set; }
    
    [Name("ReleaseYear")]
    public int? ReleaseYear { get; set; }
    
    [Name("NetworkType")]
    public string? NetworkType { get; set; }
    
    [Name("ChargingPower")]
    public string? ChargingPower { get; set; }
    
    [Name("WaterResistance")]
    public string? WaterResistance { get; set; }
    
    [Name("Material")]
    public string? Material { get; set; }
    
    [Name("Colors")]
    public string? Colors { get; set; }
    
    [Name("ColorImages")]
    public string? ColorImages { get; set; }
    
    [Name("ImageFront")]
    public string? ImageFront { get; set; }
    
    [Name("ImageBack")]
    public string? ImageBack { get; set; }
    
    [Name("ImageSide")]
    public string? ImageSide { get; set; }
    
    [Name("ImageUrl")]
    public string? ImageUrl { get; set; }
}
