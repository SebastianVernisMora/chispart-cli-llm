#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Chispart-CLI-LLM Banner Generator
Generador de banner isométrico con colores neón para Chispart
"""

import os
import sys

# Colores neón ANSI RGB 24-bit
class ChispartColors:
    # Colores Neón
    GREEN_NEON = '\033[38;2;0;255;136m'       # Verde Manzana Neón
    PURPLE_NEON = '\033[38;2;187;136;255m'    # Lila Neón
    PINK_NEON = '\033[38;2;255;136;187m'      # Rosa Neón
    CYAN_NEON = '\033[38;2;136;255;255m'      # Cian Neón
    YELLOW_NEON = '\033[38;2;255;255;136m'    # Amarillo Neón
    RED_NEON = '\033[38;2;255;136;136m'       # Rojo Neón
    
    # Colores de fondo
    BG_DARK = '\033[48;2;10;10;10m'           # Negro Profundo
    BG_GRAY = '\033[48;2;26;26;26m'           # Gris Oscuro
    
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def get_chispart_isometric_banner():
    """
    Genera el banner isométrico de Chispart-CLI-LLM
    Estilo: Isometric --filled inspirado en oh-my-logo
    """
    c = ChispartColors
    
    banner = f"""
{c.PURPLE_NEON}╔══════════════════════════════════════════════════════════════════════════════╗{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                              {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██████{c.RESET}  {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET}  {c.CYAN_NEON}██████{c.RESET}  {c.GREEN_NEON}██████{c.RESET}   {c.PURPLE_NEON}██████{c.RESET}  {c.PINK_NEON}██████{c.RESET}  {c.CYAN_NEON}██████{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}   {c.GREEN_NEON}██{c.RESET}    {c.GREEN_NEON}██{c.RESET} {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}    {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}██{c.RESET}    {c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}    {c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}    {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}    {c.CYAN_NEON}██{c.RESET}   {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}   {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}       {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}    {c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}    {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}    {c.CYAN_NEON}██{c.RESET}   {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}   {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}████████{c.RESET} {c.CYAN_NEON}██████{c.RESET}   {c.GREEN_NEON}██████{c.RESET}   {c.PURPLE_NEON}██████{c.RESET}  {c.PINK_NEON}██████{c.RESET}  {c.CYAN_NEON}██████{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}   {c.GREEN_NEON}██{c.RESET}    {c.GREEN_NEON}██{c.RESET} {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}       {c.GREEN_NEON}██{c.RESET}    {c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}    {c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}    {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}    {c.CYAN_NEON}██{c.RESET}   {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██████{c.RESET}  {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██████{c.RESET}  {c.GREEN_NEON}██{c.RESET}    {c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}    {c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}    {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██████{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                              {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                        {c.YELLOW_NEON}█████{c.RESET}  {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}                         {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                       {c.YELLOW_NEON}██{c.RESET}   {c.YELLOW_NEON}██{c.RESET} {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}                         {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                       {c.YELLOW_NEON}██{c.RESET}      {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}                         {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                       {c.YELLOW_NEON}██{c.RESET}      {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}                         {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                        {c.YELLOW_NEON}█████{c.RESET}  {c.GREEN_NEON}███████{c.RESET} {c.PURPLE_NEON}███████{c.RESET} {c.PINK_NEON}██{c.RESET}                         {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                              {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                    {c.CYAN_NEON}{c.BOLD}Universal LLM Terminal for Mobile Devices{c.RESET}                    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                           {c.YELLOW_NEON}✨ Neón Powered CLI ✨{c.RESET}                            {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                              {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}╚══════════════════════════════════════════════════════════════════════════════╝{c.RESET}
"""
    return banner

def get_chispart_3d_banner():
    """
    Banner 3D alternativo más compacto
    """
    c = ChispartColors
    
    banner = f"""
{c.GREEN_NEON}   ▄████▄   {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▄████▄{c.RESET}  {c.PURPLE_NEON}██████{c.RESET}   {c.PINK_NEON}▄████▄{c.RESET}  {c.CYAN_NEON}██████{c.RESET}
{c.GREEN_NEON}  ▐██▌  ▐██▌ {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▐██▌{c.RESET}     {c.PURPLE_NEON}██{c.RESET}   {c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}▐██▌  ▐██▌{c.RESET} {c.CYAN_NEON}██{c.RESET}   {c.CYAN_NEON}██{c.RESET}
{c.GREEN_NEON}  ▐██▌       {c.PURPLE_NEON}██████{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▐██▌{c.RESET}     {c.PURPLE_NEON}██████{c.RESET}  {c.PINK_NEON}▐██▌  ▐██▌{c.RESET} {c.CYAN_NEON}██████{c.RESET}
{c.GREEN_NEON}  ▐██▌  ▐██▌ {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▐██▌{c.RESET}     {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}▐██▌  ▐██▌{c.RESET} {c.CYAN_NEON}██{c.RESET}   {c.CYAN_NEON}██{c.RESET}
{c.GREEN_NEON}   ▀████▀   {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON} ▀████▀{c.RESET}  {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON} ▀████▀{c.RESET}  {c.CYAN_NEON}██████{c.RESET}

                    {c.YELLOW_NEON}▄████▄{c.RESET}  {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}
                   {c.YELLOW_NEON}▐██▌{c.RESET}     {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}
                   {c.YELLOW_NEON}▐██▌{c.RESET}     {c.GREEN_NEON}██{c.RESET}      {c.PURPLE_NEON}██{c.RESET}      {c.PINK_NEON}██{c.RESET}
                   {c.YELLOW_NEON}▐██▌{c.RESET}     {c.GREEN_NEON}███████{c.RESET} {c.PURPLE_NEON}███████{c.RESET} {c.PINK_NEON}██{c.RESET}
                    {c.YELLOW_NEON}▀████▀{c.RESET}

            {c.CYAN_NEON}{c.BOLD}Universal LLM Terminal for Mobile Devices{c.RESET}
                     {c.YELLOW_NEON}✨ Neón Powered CLI ✨{c.RESET}
"""
    return banner

def get_chispart_minimal_banner():
    """
    Banner minimalista para espacios reducidos
    """
    c = ChispartColors
    
    banner = f"""
{c.GREEN_NEON}  ▄████▄ {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▄████▄{c.RESET}  {c.PURPLE_NEON}██████{c.RESET}  {c.PINK_NEON}▄████▄{c.RESET}  {c.CYAN_NEON}██████{c.RESET}
{c.GREEN_NEON} ▐██▌    {c.PURPLE_NEON}██████{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▐██▌{c.RESET}     {c.PURPLE_NEON}██████{c.RESET}  {c.PINK_NEON}▐██▌  ▐██▌{c.RESET} {c.CYAN_NEON}██████{c.RESET}
{c.GREEN_NEON} ▐██▌    {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}▐██▌{c.RESET}     {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}▐██▌  ▐██▌{c.RESET} {c.CYAN_NEON}██{c.RESET}   {c.CYAN_NEON}██{c.RESET}
{c.GREEN_NEON}  ▀████▀ {c.PURPLE_NEON}██{c.RESET}  {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON} ▀████▀{c.RESET}  {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON} ▀████▀{c.RESET}  {c.CYAN_NEON}██████{c.RESET}

        {c.CYAN_NEON}Universal LLM Terminal{c.RESET} • {c.YELLOW_NEON}✨ Neón Powered ✨{c.RESET}
"""
    return banner

def get_chispart_isometric_filled():
    """
    Banner isométrico estilo --filled más elaborado
    Inspirado en oh-my-logo con efectos 3D
    """
    c = ChispartColors
    
    banner = f"""
{c.PURPLE_NEON}╔════════════════════════════════════════════════════════════════════════════════╗{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                                {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}     {c.GREEN_NEON}███████{c.RESET}  {c.PURPLE_NEON}██{c.RESET}   {c.PINK_NEON}██{c.RESET}  {c.CYAN_NEON}███████{c.RESET}  {c.GREEN_NEON}███████{c.RESET}   {c.PURPLE_NEON}███████{c.RESET}  {c.PINK_NEON}███████{c.RESET}  {c.CYAN_NEON}███████{c.RESET}     {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██{c.RESET}░░░░░{c.GREEN_NEON}██{c.RESET} {c.PURPLE_NEON}██{c.RESET}   {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░{c.CYAN_NEON}██{c.RESET} {c.GREEN_NEON}██{c.RESET}░░░░░{c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}░░░░░{c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}░░░░░{c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░{c.CYAN_NEON}██{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██{c.RESET}░░░░░░░  {c.PURPLE_NEON}██{c.RESET}   {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░░░  {c.GREEN_NEON}██{c.RESET}░░░░░░░   {c.PURPLE_NEON}██{c.RESET}░░░░░{c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}░░░░░{c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░{c.CYAN_NEON}██{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██{c.RESET}░░░░░░░  {c.PURPLE_NEON}███████{c.RESET}  {c.CYAN_NEON}███████{c.RESET}   {c.GREEN_NEON}███████{c.RESET}    {c.PURPLE_NEON}███████{c.RESET}  {c.PINK_NEON}███████{c.RESET}  {c.CYAN_NEON}███████{c.RESET}     {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}    {c.GREEN_NEON}██{c.RESET}░░░░░{c.GREEN_NEON}██{c.RESET} {c.PURPLE_NEON}██{c.RESET}   {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░░░  {c.GREEN_NEON}██{c.RESET}░░░░░{c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}░░░░░{c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}░░░░░{c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}██{c.RESET}░░░░░{c.CYAN_NEON}██{c.RESET}    {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}     {c.GREEN_NEON}███████{c.RESET}  {c.PURPLE_NEON}██{c.RESET}   {c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}███████{c.RESET}  {c.GREEN_NEON}██{c.RESET}░░░░░{c.GREEN_NEON}██{c.RESET}  {c.PURPLE_NEON}██{c.RESET}░░░░░{c.PURPLE_NEON}██{c.RESET} {c.PINK_NEON}██{c.RESET}░░░░░{c.PINK_NEON}██{c.RESET} {c.CYAN_NEON}███████{c.RESET}     {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                                {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                         {c.YELLOW_NEON}██████{c.RESET}   {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}██{c.RESET}                          {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                        {c.YELLOW_NEON}██{c.RESET}░░░░{c.YELLOW_NEON}██{c.RESET}  {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}██{c.RESET}                          {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                        {c.YELLOW_NEON}██{c.RESET}░░░░░░░  {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}██{c.RESET}                          {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                        {c.YELLOW_NEON}██{c.RESET}░░░░░░░  {c.GREEN_NEON}██{c.RESET}       {c.PURPLE_NEON}██{c.RESET}       {c.PINK_NEON}██{c.RESET}                          {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                         {c.YELLOW_NEON}██████{c.RESET}   {c.GREEN_NEON}████████{c.RESET} {c.PURPLE_NEON}████████{c.RESET} {c.PINK_NEON}██{c.RESET}                          {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                                {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                     {c.CYAN_NEON}{c.BOLD}Universal LLM Terminal for Mobile Devices{c.RESET}                     {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                            {c.YELLOW_NEON}✨ Neón Powered CLI ✨{c.RESET}                             {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}║{c.RESET}                                                                                {c.PURPLE_NEON}║{c.RESET}
{c.PURPLE_NEON}╚════════════════════════════════════════════════════════════════════════════════╝{c.RESET}
"""
    return banner

def print_banner(style="isometric"):
    """
    Imprime el banner según el estilo especificado
    """
    if style == "isometric":
        print(get_chispart_isometric_banner())
    elif style == "3d":
        print(get_chispart_3d_banner())
    elif style == "minimal":
        print(get_chispart_minimal_banner())
    elif style == "filled":
        print(get_chispart_isometric_filled())
    else:
        print(get_chispart_isometric_banner())

def print_welcome_info():
    """
    Imprime información de bienvenida después del banner
    """
    c = ChispartColors
    
    info = f"""
{c.CYAN_NEON}🚀 Bienvenido a Chispart-CLI-LLM{c.RESET}

{c.GREEN_NEON}📱 Comandos rápidos:{c.RESET}
  {c.YELLOW_NEON}chispart chat 'mensaje'{c.RESET}     - Enviar mensaje
  {c.YELLOW_NEON}chispart interactivo{c.RESET}        - Modo chat interactivo
  {c.YELLOW_NEON}chispart imagen foto.jpg{c.RESET}    - Analizar imagen
  {c.YELLOW_NEON}chispart pdf documento.pdf{c.RESET}  - Analizar PDF

{c.PURPLE_NEON}🔧 Comandos de sistema:{c.RESET}
  {c.YELLOW_NEON}chispart --help{c.RESET}             - Ayuda completa
  {c.YELLOW_NEON}chispart-ui{c.RESET}                 - Interfaz web
  {c.YELLOW_NEON}chispart-service{c.RESET}            - Gestión de servicio

{c.PINK_NEON}⚡ Comandos súper cortos:{c.RESET}
  {c.YELLOW_NEON}chs{c.RESET}                         - Comando principal
  {c.YELLOW_NEON}chs-ui{c.RESET}                      - Interfaz web
  {c.YELLOW_NEON}chs-start{c.RESET}                   - Iniciar servicio

{c.CYAN_NEON}💡 Ejemplo:{c.RESET} {c.GREEN_NEON}chs chat '¿Cuál es la capital de Francia?'{c.RESET}

{c.DIM}🌐 Más info: https://github.com/SebastianVernisMora/chispart-cli-llm{c.RESET}
"""
    print(info)

def main():
    """
    Función principal para testing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Chispart Banner Generator')
    parser.add_argument('--style', choices=['isometric', '3d', 'minimal', 'filled'], 
                       default='filled', help='Estilo del banner')
    parser.add_argument('--no-info', action='store_true', help='No mostrar información adicional')
    
    args = parser.parse_args()
    
    print_banner(args.style)
    
    if not args.no_info:
        print_welcome_info()

if __name__ == "__main__":
    main()