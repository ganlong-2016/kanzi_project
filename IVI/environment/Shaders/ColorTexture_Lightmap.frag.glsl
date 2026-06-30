uniform sampler2D Texture;
uniform sampler2D Lightmap;
uniform lowp float lightmapStrength;
uniform lowp float BlendIntensity;
uniform lowp vec4 Ambient;
varying mediump vec2 vTexCoord;
varying mediump vec2 vTexCoord1;

void main()
{
    precision lowp float;

    vec4 color = texture2D(Texture, vTexCoord);
    vec4 lightmapcolor = texture2D(Lightmap, vTexCoord1) * lightmapStrength;
    gl_FragColor.rgba = ( color.rgba  * Ambient * lightmapcolor + lightmapcolor) * BlendIntensity ;
}
