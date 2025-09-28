using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MobilePhoneAPI.Migrations
{
    /// <inheritdoc />
    public partial class AddColorImagesField : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ColorImages",
                table: "Phones",
                type: "character varying(2000)",
                maxLength: 2000,
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ColorImages",
                table: "Phones");
        }
    }
}
