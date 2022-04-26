<?xml version="1.0"?>
<!--
An experimental Qt Designer form conversion stylesheet.

Copyright (C) 2005 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:set="http://exslt.org/sets"
  xmlns:math="http://exslt.org/math"
  xmlns:template="http://www.boddie.org.uk/ns/xmltools/template">

  <xsl:output indent="yes"/>



  <!-- Start at the top, producing a template file. -->

  <xsl:template match="UI">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title><xsl:value-of select="widget/property[@name='caption']/string/text()"/></title>
        <link xmlns:xlink="http://www.w3.org/1999/xlink" href="styles/styles.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="scripts/sarissa.js"> </script>
        <script type="text/javascript" src="scripts/XSLForms.js"> </script>
      </head>
      <body>
        <form method="post">
          <xsl:apply-templates select="widget"/>
        </form>
      </body>
    </html>
  </xsl:template>



  <!-- Reproduce the layout. -->

  <xsl:template match="grid">
    <xsl:variable name="grid" select="."/>
    <table xmlns="http://www.w3.org/1999/xhtml" width="100%">
      <!-- Get the row numbers in ascending order. -->
      <xsl:for-each select="set:distinct($grid/*/@row)">
        <xsl:sort select="." data-type="number" order="ascending"/>
        <xsl:variable name="row" select="."/>
        <tr>
          <!-- Get all elements in the row, ordered by column number. -->
          <xsl:call-template name="grid-column">
            <xsl:with-param name="column" select="math:min($grid/*[@row=$row]/@column)"/>
            <xsl:with-param name="row" select="$row"/>
            <xsl:with-param name="grid" select="$grid"/>
            <xsl:with-param name="last-column">-1</xsl:with-param>
          </xsl:call-template>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template name="grid-column">
    <xsl:param name="column"/>
    <xsl:param name="row"/>
    <xsl:param name="grid"/>
    <xsl:param name="last-column"/>
    <xsl:param name="last-colspan">1</xsl:param>
    <!-- Insert missing cells. -->
    <xsl:if test="$column != $last-column + $last-colspan">
      <xsl:variable name="spanned-columns" select="$grid/*[$row > @row and @row + @rowspan > $row and @column > $last-column and $column > @column]/@column"/>
      <xsl:choose>
        <xsl:when test="count($spanned-columns) != 0">
          <xsl:variable name="last-spanned-column" select="math:highest($spanned-columns)"/>
          <xsl:variable name="last-spanned-colspan" select="$last-spanned-column/../@colspan"/>
          <xsl:if test="$column != $last-spanned-column + $last-spanned-colspan">
            <td colspan="{$column - $last-spanned-column - $last-spanned-colspan}" xmlns="http://www.w3.org/1999/xhtml">
            </td>
          </xsl:if>
        </xsl:when>
        <xsl:otherwise>
          <td colspan="{$column - $last-column - $last-colspan}" xmlns="http://www.w3.org/1999/xhtml">
          </td>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <!-- Remember useful information. -->
    <xsl:variable name="this-column" select="$grid/*[@row=$row and @column=$column]"/>
    <xsl:variable name="this-colspan" select="$this-column/@colspan"/>
    <!-- Insert this cell. -->
    <td xmlns="http://www.w3.org/1999/xhtml">
      <!-- Add colspan and rowspan details. -->
      <xsl:apply-templates select="$this-colspan|$this-column/@rowspan"/>
      <!-- Transform the element. -->
      <xsl:apply-templates select="$this-column"/>
    </td>
    <!-- Find remaining cells in this row. -->
    <xsl:if test="count($grid/*[@row=$row and @column > $column]) > 0">
      <xsl:choose>
        <xsl:when test="$this-colspan">
          <xsl:call-template name="grid-column">
            <xsl:with-param name="column" select="math:min($grid/*[@row=$row and @column > $column]/@column)"/>
            <xsl:with-param name="row" select="$row"/>
            <xsl:with-param name="grid" select="$grid"/>
            <xsl:with-param name="last-column" select="$column"/>
            <xsl:with-param name="last-colspan" select="$this-colspan"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="grid-column">
            <xsl:with-param name="column" select="math:min($grid/*[@row=$row and @column > $column]/@column)"/>
            <xsl:with-param name="row" select="$row"/>
            <xsl:with-param name="grid" select="$grid"/>
            <xsl:with-param name="last-column" select="$column"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="spacer">
  </xsl:template>

  <xsl:template match="vbox">
    <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
  </xsl:template>

  <xsl:template match="hbox">
    <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
  </xsl:template>

  <xsl:template match="widget">
    <xsl:apply-templates select="property[@name='geometry']"/>
    <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
  </xsl:template>

  <!-- Container widgets. -->

  <xsl:template match="widget[@class='QFrame']">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:attribute name="template:element"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:apply-templates select="property[@name='geometry']"/>
      <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
    </div>
  </xsl:template>

  <xsl:template match="widget[@class='QTabWidget']">
    <xsl:variable name="name-prop" select="property[@name='name']"/>
    <xsl:attribute name="template:element"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
    <xsl:apply-templates select="property[@name='geometry']"/>
    <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
  </xsl:template>

  <xsl:template match="widget[@class='QWidgetStack']">
    <xsl:variable name="name-prop" select="property[@name='name']"/>
    <xsl:attribute name="template:element"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
    <xsl:apply-templates select="property[@name='geometry']"/>
    <xsl:apply-templates select="*[not(local-name() = 'property')]"/>
  </xsl:template>

  <xsl:template match="widget[@class='QWidget']">
    <!-- NOTE: Suppress overriding of names. -->
    <xsl:if test="not(../@class) or ../@class != 'QTabWidget'">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:attribute name="template:element"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
    </xsl:if>
    <xsl:apply-templates select="property[@name='geometry']"/>
    <xsl:apply-templates select="*[not(local-name() = 'property') and not(local-name() = 'attribute')]"/>
  </xsl:template>

  <!-- Specific widgets. -->

  <xsl:template match="widget[@class='QComboBox']">
    <select xmlns="http://www.w3.org/1999/xhtml">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="field-name" select="$name-prop/cstring/text()"/>
      <!-- NOTE: Adding _enum suffix. -->
      <xsl:variable name="enum-name" select="concat($name-prop/cstring/text(), '_enum')"/>
      <xsl:attribute name="template:multiple-choice-field"><xsl:value-of select="$field-name"/>,value</xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="$field-name"/></xsl:attribute>
      <xsl:apply-templates select="item">
        <xsl:with-param name="enum-name" select="$enum-name"/>
      </xsl:apply-templates>
    </select>
  </xsl:template>

  <xsl:template match="widget[@class='QListBox']">
    <select xmlns="http://www.w3.org/1999/xhtml" multiple="multiple">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="field-name" select="$name-prop/cstring/text()"/>
      <!-- NOTE: Adding _enum suffix. -->
      <xsl:variable name="enum-name" select="concat($name-prop/cstring/text(), '_enum')"/>
      <xsl:attribute name="template:multiple-choice-list-field"><xsl:value-of select="$field-name"/>,<xsl:value-of select="$enum-name"/></xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="$field-name"/></xsl:attribute>
      <xsl:apply-templates select="item">
        <xsl:with-param name="enum-name" select="$enum-name"/>
        <xsl:with-param name="item-type">list</xsl:with-param>
      </xsl:apply-templates>
    </select>
  </xsl:template>

  <xsl:template match="item">
    <xsl:param name="enum-name"/>
    <xsl:param name="item-type"/>
    <option xmlns="http://www.w3.org/1999/xhtml">
      <xsl:choose>
        <xsl:when test="$item-type = 'list'">
          <xsl:attribute name="template:multiple-choice-list-value"><xsl:value-of select="$enum-name"/>,value,selected</xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="template:multiple-choice-value"><xsl:value-of select="$enum-name"/>,value,selected</xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:variable name="value-prop" select="property[@name='text']"/>
      <xsl:attribute name="value"><xsl:value-of select="$value-prop/string/text()"/></xsl:attribute>
      <xsl:value-of select="$value-prop/string/text()"/>
    </option>
  </xsl:template>

  <xsl:template match="widget[@class='QLabel']">
    <xsl:variable name="value-prop" select="property[@name='text']"/>
    <!-- NOTE: Permitting element generation from the text. -->
    <xsl:value-of disable-output-escaping="yes" select="$value-prop/string/text()"/>
  </xsl:template>

  <xsl:template match="widget[@class='QPushButton']">
    <input xmlns="http://www.w3.org/1999/xhtml" type="submit">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="field-name" select="$name-prop/cstring/text()"/>
      <xsl:variable name="value-prop" select="property[@name='text']"/>
      <xsl:choose>
        <xsl:when test="starts-with($field-name, 'add_')">
          <xsl:variable name="affected-element" select="substring-after($field-name, 'add_')"/>
          <xsl:attribute name="template:selector-field"><xsl:value-of select="$field-name"/>,<xsl:value-of select="$affected-element"/></xsl:attribute>
        </xsl:when>
        <xsl:when test="starts-with($field-name, 'remove_')">
          <xsl:variable name="affected-element" select="substring-after($field-name, 'remove_')"/>
          <xsl:attribute name="template:selector-field"><xsl:value-of select="$field-name"/>,<xsl:value-of select="$affected-element"/></xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="template:selector-field"><xsl:value-of select="$field-name"/></xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:attribute name="name"><xsl:value-of select="$field-name"/></xsl:attribute>
      <xsl:attribute name="value"><xsl:value-of select="$value-prop/string/text()"/></xsl:attribute>
    </input>
  </xsl:template>

  <xsl:template match="widget[@class='QLineEdit']">
    <input xmlns="http://www.w3.org/1999/xhtml" type="text">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="value-prop" select="property[@name='text']"/>
      <xsl:attribute name="template:attribute-field"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:attribute name="value"><xsl:value-of select="$value-prop/string/text()"/></xsl:attribute>
    </input>
  </xsl:template>

  <xsl:template match="widget[@class='QTextEdit']">
    <textarea xmlns="http://www.w3.org/1999/xhtml">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="value-prop" select="property[@name='text']"/>
      <xsl:attribute name="template:attribute-area"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:value-of select="$value-prop/string/text()"/>
    </textarea>
  </xsl:template>

  <xsl:template match="widget[@class='QRadioButton']">
    <input xmlns="http://www.w3.org/1999/xhtml" type="radio">
      <xsl:variable name="name-prop" select="property[@name='name']"/>
      <xsl:variable name="value-prop" select="property[@name='text']"/>
      <xsl:attribute name="template:attribute-field"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:attribute name="name"><xsl:value-of select="$name-prop/cstring/text()"/></xsl:attribute>
      <xsl:attribute name="value"><xsl:value-of select="$value-prop/string/text()"/></xsl:attribute>
    </input>
  </xsl:template>



  <!-- Geometry. -->

  <xsl:template match="property[@name='geometry']">
    <xsl:apply-templates select="rect/*[1]">
      <xsl:with-param name="style">position: absolute</xsl:with-param>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template name="make-geometry">
    <xsl:param name="style"/>
    <xsl:variable name="dimension" select="following-sibling::*[1]"/>
    <xsl:choose>
      <xsl:when test="not($dimension)">
        <xsl:attribute name="style"><xsl:value-of select="$style"/></xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="$dimension">
          <xsl:with-param name="style" select="$style"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="x">
    <xsl:param name="style"/>
    <xsl:call-template name="make-geometry">
      <xsl:with-param name="style"><xsl:value-of select="$style"/>; left: <xsl:value-of select="text()"/>px</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="y">
    <xsl:param name="style"/>
    <xsl:call-template name="make-geometry">
      <xsl:with-param name="style"><xsl:value-of select="$style"/>; top: <xsl:value-of select="text()"/>px</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="width">
    <xsl:param name="style"/>
    <xsl:call-template name="make-geometry">
      <xsl:with-param name="style"><xsl:value-of select="$style"/>; width: <xsl:value-of select="text()"/>px</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="height">
    <xsl:param name="style"/>
    <xsl:call-template name="make-geometry">
      <xsl:with-param name="style"><xsl:value-of select="$style"/>; height: <xsl:value-of select="text()"/>px</xsl:with-param>
    </xsl:call-template>
  </xsl:template>



  <!-- Identification. -->

  <xsl:template match="property[@name='name']">
  </xsl:template>



  <!-- Labels and values. -->

  <xsl:template match="property[@name='text']">
  </xsl:template>



  <!-- Captions. -->

  <xsl:template match="property[@name='caption']">
  </xsl:template>



  <!-- Copy attributes. -->

  <xsl:template match="@*">
    <xsl:copy>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
