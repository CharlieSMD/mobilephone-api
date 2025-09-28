using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MobilePhoneAPI.Models;

public class Favorite
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    public int UserId { get; set; }
    
    [Required]
    public int PhoneId { get; set; }
    
    [Required]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // Navigation properties
    [ForeignKey("UserId")]
    public virtual User User { get; set; } = null!;
    
    [ForeignKey("PhoneId")]
    public virtual Phone Phone { get; set; } = null!;
}
