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
    
    public decimal Price { get; set; }
    
    [MaxLength(255)]
    public string ImageUrl { get; set; } = string.Empty;
} 