uniform sampler2D Texture;
uniform lowp float BlendIntensity;
uniform lowp vec4 Ambient;
uniform lowp vec4 Ambient2;
varying mediump vec2 vTexCoord;
varying mediump vec2 vTexCoord1;


void main()
{
    precision lowp float;

    vec4 color = texture2D(Texture, vTexCoord);
    vec4 a_mask = texture2D(Texture, vTexCoord1);
    vec4 col_a = Ambient * (1.0 - a_mask.r) + Ambient2 * (a_mask.r);
    
    gl_FragColor.rgb = color.rgb * col_a.rgb * BlendIntensity;
    gl_FragColor.a = color.r * BlendIntensity;
}
