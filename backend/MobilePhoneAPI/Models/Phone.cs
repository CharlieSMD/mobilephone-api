using System.ComponentModel.DataAnnotations;

namespace MobilePhoneAPI.Models;

public class Phone
{
    public int Id { get; set; }
    
    [Required]
    [MaxLength(50)]
    public string Brand { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(100)]
    public string Model { get; set; } = string.Empty;
    
    [MaxLength(50)]
    public string Storage { get; set; } = string.Empty;
    
    [MaxLength(20)]
    public string Ram { get; set; } = string.Empty;
    
    [MaxLength(20)]
    public string ScreenSize { get; set; } = string.Empty;
    
    [MaxLength(100)]
    public string Camera { get; set; } = string.Empty;
    
    [MaxLength(20)]
    public string Battery { get; set; } = string.Empty;
    
    [MaxLength(255)]
    public string ImageUrl { get; set; } = string.Empty;
    
    // New fields for detailed specifications
    public decimal? Weight { get; set; } // Weight in grams
    
    [MaxLength(100)]
    public string? Dimensions { get; set; } // Format: "L x W x H mm"
    
    [MaxLength(200)]
    public string? Processor { get; set; }
    
    [MaxLength(100)]
    public string? Os { get; set; }
    
    public int? ReleaseYear { get; set; }
    
    [MaxLength(100)]
    public string? NetworkType { get; set; }
    
    [MaxLength(100)]
    public string? ChargingPower { get; set; }
    
    [MaxLength(100)]
    public string? WaterResistance { get; set; }
    
    [MaxLength(200)]
    public string? Material { get; set; }
    
    [MaxLength(200)]
    public string? Colors { get; set; } // Comma-separated color options
    
    // Image fields
    [MaxLength(255)]
    public string? ImageFront { get; set; }
    
    [MaxLength(255)]
    public string? ImageBack { get; set; }
    
    [MaxLength(255)]
    public string? ImageSide { get; set; }
} 